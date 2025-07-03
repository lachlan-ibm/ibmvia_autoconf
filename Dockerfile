FROM registry.access.redhat.com/ubi8/ubi-micro:latest

RUN microdnf install python3 python3-pip && pip3 install ibmvia_autoconf

LABEL version="1.0"

Label description="Python runtime set up to perform automated configuration of IBM Verify Identity Access deployments."

Label ibm.security.image.author="Lachlan Gleeson"

CMD ["/usr/local/bin/python3", "-m", "ibmvia_autoconf"]