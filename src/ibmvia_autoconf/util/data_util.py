#!/bin/python
"""
@copyright: IBM
"""
import os
import yaml
import base64
import pathlib
import logging
import sys
import tempfile
import atexit

from copy import deepcopy
from . import constants as const
from .logging_util import setup_logging

setup_logging()
_logger = logging.getLogger(__name__)


def get_k8s_pod_namespace():
    """
    Get the default Kubernetes namespace from the serviceaccount file.
    
    Returns: Namespace string
    
    Raises:
        RuntimeError: If namespace file cannot be read or is invalid
    """
    
    namespace_file = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
    try:
        with open(namespace_file, 'r') as f:
            namespace = f.read().strip()
            if not namespace:
                raise RuntimeError(
                    f"Namespace file '{namespace_file}' is empty. "
                    "Cannot determine default namespace for Kubernetes resources."
                )
            return namespace
    except FileNotFoundError:
        raise RuntimeError(
            f"Namespace file '{namespace_file}' not found. "
            "Cannot determine default namespace. "
            "Use explicit format 'namespace/name:key' and ensure running in Kubernetes."
        ) from None
    except (IOError, OSError) as e:
        raise RuntimeError(
            f"Failed to read namespace file '{namespace_file}': {e}. "
            "Cannot determine default namespace for Kubernetes resources."
        ) from e


def to_camel_case(snake_case):
    parts = snake_case.split('_')
    return parts[0] + ''.join(x.title() for x in parts[1:])

def remap_keys(data_dict: dict, remap_dict: dict) -> dict:
    '''
    old_dict: dictionary with keys to be remapped
    remap_dict: dictionary with mapping {old_key: new_key}
    '''
    if not isinstance(data_dict, dict) or not isinstance(remap_dict, dict):
        raise TypeError("give me dictionaries")
    return {remap_dict.get(k, k): v for k, v in data_dict.items()}

def prefix_keys(data_dict, source_key, prefix):
    '''
    data_dict: dictionary to modify
    source_key: key of nested dictionary to flatten
    prefix: string to prepend to keys of nested dictionary

    function modifies the data_dict to add the prefix string the to beginning
    of all the keys in the source_key dictionary
    '''
    if source_key in data_dict and isinstance(data_dict[source_key], dict):
        data_dict.update({prefix + k: v for k, v in data_dict.pop(source_key).items()})

#Method guaranteed to return a list with at least dictionary in it (if its not empty)
def optional_list(x):
    if isinstance(x, list) and len(x) > 0:
        return x
    else:
        return [{}]

#Filter a list of dicts on a given key for a given value
def filter_list(attribute, value, _list):
    return list(filter(lambda x: attribute in x and x[attribute] == value, _list))

class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for a in args:
            if isinstance(a, dict):
                for k, v in a.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    elif isinstance(v, list):
                        mapList = []
                        for element in v:
                            if isinstance(element, dict) or isinstance(element, list):
                                mapList += [Map(element)]
                            else:
                                mapList += [element]
                        v = mapList
                    self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                if isinstance(v, list):
                    kwList = []
                    for element in v:
                        if isinstance(element, dict) or isinstance(element, list):
                            kwList += [Map(element)]
                        else:
                            kwList += [element]
                    v = kwList
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr, None)

    def __setattr__(self, attr, value):
        self.__setitem__(attr, value)

    def __setitem__(self, k, v):
        super(Map, self).__setitem__(k, v)
        self.__dict__.update({k: v})

    def __delitem__(self, k):
        super(Map, self).__delitem__(k)
        del self.__dict__[k]

    def __deepcopy__(self, memo=None):
        return Map(deepcopy(dict(self), memo=memo)) 


class CustomLoader(yaml.SafeLoader):

    k8s_cache = {}
    _temp_files = []  # Track temp files for cleanup
    _temp_dirs = []  # Track temp directories for cleanup
    _cleanup_registered = False
    _default_namespace = None  # Cache for default namespace

    def __init__(self, path):
        self.k8s_cache = {}
        self._root = os.path.split(path.name)[0]
        self._kube_client = None
        super(CustomLoader, self).__init__(path)
        CustomLoader.add_constructor('!include', CustomLoader.include)
        CustomLoader.add_constructor('!secret', CustomLoader.k8s_secret)
        CustomLoader.add_constructor('!secret:tofile', CustomLoader.k8s_secret_tofile)
        CustomLoader.add_constructor('!configmap:tofile', CustomLoader.k8s_configmap_tofile)
        CustomLoader.add_constructor('!environment', CustomLoader.env_secret)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, CustomLoader)

    def k8s_secret(self, node):
        secret = self.construct_scalar(node)
        #Split secret into name and key
        namespaceName, key = secret.split(':')
        k8sSecret = self.k8s_cache.get(namespaceName, None)
        self._ensure_kube_client();assert self._kube_client is not None# Type narrowing: _ensure_kube_client raises if None
        if k8sSecret == None:
            # Check if namespace is explicitly provided (format: namespace/name)
            # If not, use the pod's namespace (format: name)
            if '/' in namespaceName:
                namespace, name = namespaceName.split('/')
            else:
                namespace = get_k8s_pod_namespace()
                name = namespaceName
            #Use k8s API to look up secret
            k8sSecret = self._kube_client.CoreV1Api().read_namespaced_secret(name, namespace)
            self.k8s_cache[namespaceName] = k8sSecret
        if k8sSecret is None or not hasattr(k8sSecret, 'data'):
            raise RuntimeError("Uknown secret object {}".format(secret))
        data = getattr(k8sSecret, 'data', {})
        return base64.b64decode(data[key]).decode()

    def env_secret(self, node):
        try:
            return os.environ.get(self.construct_scalar(node))
        except KeyError as e:
            raise ValueError("Environment variable {} does not exist".format(
                                                self.construct_scalar(node))) from e

    def k8s_secret_tofile(self, node):
        """
        Load a Kubernetes Secret and write to temp file.
        
        Returns the temp file path string that can be passed to FILE_LOADER.read_file().
        
        Format: !secret:tofile namespace/name:key
        """
        return self._k8s_resource_tofile(node, resource_type='secret')

    def k8s_configmap_tofile(self, node):
        """
        Load a Kubernetes ConfigMap and write to temp file.
        
        Format: !configmap:tofile namespace/name:key
        """
        return self._k8s_resource_tofile(node, resource_type='configmap')


    def _get_default_namespace(self):
        """
        Get the default Kubernetes namespace from the serviceaccount file.
        
        Returns: Namespace string
        
        Raises:
            RuntimeError: If namespace file cannot be read or is invalid
        """
        if CustomLoader._default_namespace is not None:
            return CustomLoader._default_namespace
        
        CustomLoader._default_namespace = get_k8s_pod_namespace()
        return CustomLoader._default_namespace

    def _validate_k8s_tofile_resource(self, resource_type, node):
        # Validate resource type early (fail-fast)
        VALID_RESOURCE_TYPES = ('secret', 'configmap')
        if resource_type not in VALID_RESOURCE_TYPES:
            raise ValueError(
                f"Unknown resource type: '{resource_type}'. "
                f"Valid types: {', '.join(VALID_RESOURCE_TYPES)}"
            )
        
        # Parse and validate resource reference
        resource_ref = self.construct_scalar(node)
        try:
            namespaceName, key = resource_ref.split(':', 1)
            if '/' not in namespaceName:
                # No namespace provided, use default from container
                default_ns = self._get_default_namespace()
                namespaceName = f"{default_ns}/{namespaceName}"
        except ValueError:
            raise ValueError(
                f"Invalid {resource_type}:tofile format: '{resource_ref}'. "
                f"Expected: 'namespace/name:key' or 'name:key' (uses container namespace)"
            ) from None
        return namespaceName, key


    def _k8s_resource_tofile(self, node, resource_type='secret'):
        """
        Internal method to load K8s Secret or ConfigMap and write to temp file.
        
        Args:
            node: YAML node containing the resource reference
            resource_type: Either 'secret' or 'configmap'
        
        Returns: Temp file path string
        
        Raises:
            ValueError: If resource_ref format is invalid or resource_type is unknown
            RuntimeError: If Kubernetes client not found or resource not found
        """
        namespaceName, key = self._validate_k8s_tofile_resource(resource_type, node)
        temp_path = os.path.join(
            tempfile.gettempdir(),
            base64.urlsafe_b64encode(namespaceName.encode('utf-8')).decode('utf-8'),
            key
        )
        if temp_path in CustomLoader._temp_files:
            return temp_path
        
        self._ensure_kube_client()
        
        k8sResource = self._get_cached_or_fetch_resource(resource_type, namespaceName)
        contents = self._extract_resource_data(k8sResource, key, resource_type, namespaceName)
        temp_path = self._write_to_unique_temp_file(namespaceName, key, contents)
        
        self._register_temp_file_cleanup(temp_path)
        return temp_path
    
    def _ensure_kube_client(self):
        """Initialize Kubernetes client if not already cached."""
        if self._kube_client is None:
            self._kube_client = get_kube_client()
            if not self._kube_client:
                raise RuntimeError("Kubernetes client not found")
    
    def _get_cached_or_fetch_resource(self, resource_type, namespaceName):
        """Get resource from cache or fetch from K8s API."""
        cache_key = f"{resource_type}:{namespaceName}"
        k8sResource = self.k8s_cache.get(cache_key)
        
        if k8sResource is None:
            namespace, name = namespaceName.split('/', 1)
            try:
                k8sResource = self._fetch_k8s_resource(resource_type, name, namespace)
            except Exception as e:
                raise RuntimeError(
                    f"{resource_type.capitalize()} not found: {namespaceName}"
                ) from e
            self.k8s_cache[cache_key] = k8sResource
        
        return k8sResource
    
    def _extract_resource_data(self, k8sResource, key, resource_type, namespaceName):
        """Extract and decode data from K8s resource."""
        data = getattr(k8sResource, 'data', {})
        if key not in data:
            raise RuntimeError(
                f"Key '{key}' not found in {resource_type} {namespaceName}"
            )
        return base64.b64decode(data[key])
    
    def _write_to_unique_temp_file(self, namespaceName, key, contents):
        """
        Write contents to a temp file in a unique directory.
        
        Creates a directory based on base64-encoded namespaceName,
        then writes the file with the exact key name.
        """
        dir_name = base64.urlsafe_b64encode(namespaceName.encode('utf-8')).decode('utf-8')
        unique_dir = os.path.join(tempfile.gettempdir(), dir_name)
        os.makedirs(unique_dir, exist_ok=True)
        CustomLoader._temp_dirs.append(unique_dir)
        
        temp_path = os.path.join(unique_dir, key)
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        return temp_path
    
    def _register_temp_file_cleanup(self, temp_path):
        """Track temp file and register cleanup handler."""
        CustomLoader._temp_files.append(temp_path)
        if not CustomLoader._cleanup_registered:
            atexit.register(CustomLoader._cleanup_temp_files)
            CustomLoader._cleanup_registered = True
    
    def _fetch_k8s_resource(self, resource_type, name, namespace):
        """
        Fetch a Kubernetes resource by type.
        
        Args:
            resource_type: Either 'secret' or 'configmap'
            name: Resource name
            namespace: Kubernetes namespace
        
        Returns: Kubernetes resource object
        
        Note:
            This method assumes self._kube_client is already initialized.
            It should only be called after verifying the client exists.
        """
        # Type assertion: _kube_client is guaranteed to be non-None when this is called
        assert self._kube_client is not None, "Kubernetes client must be initialized"
        api = self._kube_client.CoreV1Api()
        fetchers = {
            'secret': api.read_namespaced_secret,
            'configmap': api.read_namespaced_config_map
        }
        return fetchers[resource_type](name, namespace)

    @staticmethod
    def _cleanup_temp_files():
        """Clean up all temp files on exit."""
        for path in CustomLoader._temp_files:
            try:
                os.unlink(path)
            except (OSError, FileNotFoundError):
                pass
        for dir_path in set(CustomLoader._temp_dirs):
            try:
                os.rmdir(dir_path)
            except OSError:
                pass

class FileLoader():

    def __init__(self, config_base_dir=None):
        self.config_base_dir = config_base_dir if config_base_dir else str(pathlib.Path.home())
        if self.config_base_dir.endswith('/') == False:
            self.config_base_dir += '/'

    def read_files(self, paths, include_directories=False):
        result = []
        if isinstance(paths, str) == True:
            paths = [paths]
        for path in paths:
            result += self.read_file(path, include_directories=include_directories)
        return result

    def read_file(self, path, include_directories=False):
        parsed_files = []
        if not os.path.isabs(path):
            path = self.config_base_dir + path
        if os.path.isdir(path):
            if include_directories == True:
                parsed_files += [{"name": os.path.basename(path), "path": path, "type": "dir", 
                    "directory": os.path.dirname(path).replace(self.config_base_dir, '')}]
            for file_pointer in os.listdir(path):
                parsed_files += [*self.read_file(os.path.join(path, file_pointer))]
        else:
            with open(path, 'rb') as _file:
                contents = _file.read()
                result = {"name": os.path.basename(path), "contents": contents, "path": path, "type": "file",
                        "directory": os.path.dirname(path).replace(self.config_base_dir, '')}
                try:
                    result['text'] = contents.decode()
                except Exception:
                    result['text'] = 'undefined'
                parsed_files += [result]
        return parsed_files 

FILE_LOADER = FileLoader()
if const.CONFIG_BASE_DIR in os.environ.keys():
    FILE_LOADER = FileLoader(os.environ.get(const.CONFIG_BASE_DIR))
elif const.LEGACY_CONFIG_BASE_DIR in os.environ.keys():
    _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_CONFIG_BASE_DIR))
    FILE_LOADER = FileLoader(os.environ.get(const.LEGACY_CONFIG_BASE_DIR))

class IVIA_Kube_Client:
    _client = None
    _caught = False

    @classmethod
    def get_client(cls):
        if cls._client == None and cls._caught == False:
            import kubernetes
            if const.KUBERNETES_CONFIG in os.environ.keys():
                kubernetes.config.load_kube_config(config_file=os.environ.get(const.KUBERNETES_CONFIG))
            elif const.LEGACY_KUBERNETES_CONFIG in os.environ.keys():
                _logger.warn("DEPRECIATED  The {} environment variable is depreciated, use the \"IVIA\" prefix'd "
                     "properties instead".format(const.LEGACY_KUBERNETES_CONFIG))
                kubernetes.config.load_kube_config(config_file=os.environ.get(const.LEGACY_KUBERNETES_CONFIG))
            elif cls._caught == False:
                try:
                    kubernetes.config.load_config()
                except:
                    cls._caught = True
            cls._client = kubernetes.client
        return cls._client

def get_kube_client():
    return IVIA_Kube_Client.get_client()

KUBE_CLIENT_SLEEP = 15
try:
    if const.KUBERNETES_CLIENT_SLEEP in os.environ.keys():
        KUBE_CLIENT_SLEEP = int(os.environ.get(const.KUBERNETES_CLIENT_SLEEP, 15))
    elif const.LEGACY_KUBERNETES_CLIENT_SLEEP in os.environ.keys():
        KUBE_CLIENT_SLEEP = int(os.environ.get(const.LEGACY_KUBERNETES_CLIENT_SLEEP, 15))
except ValueError:
    KUBE_CLIENT_SLEEP = 15

PUBLISH_SNAPSHOT_SLEEP = 3
if const.PUBLISH_SNAPSHOT_SLEEP in os.environ.keys():
    PUBLISH_SNAPSHOT_SLEEP = int(os.environ.get(const.PUBLISH_SNAPSHOT_SLEEP, 3))
