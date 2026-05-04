#!/bin/bash
# Generate HTML documentation from JSON schemas

set -e

SCHEMA_DIR="schemas"
OUTPUT_DIR="schema_html"
STATIC_DIR="_static"
CONFIG_FILE="schema_config.yaml"

echo "Generating JSON Schema documentation..."

# Create output directory
mkdir -p "$OUTPUT_DIR"
mkdir -p "$STATIC_DIR"

# Generate documentation for each module
for module in base access_control federation appliance container webseal; do
    echo "  Processing $module module..."
    
    # Create output directory for this module
    mkdir -p "$OUTPUT_DIR/$module"
    
    # Process each JSON file individually
    for schema_file in "$SCHEMA_DIR/$module/"*.json; do
        if [ -f "$schema_file" ]; then
            filename=$(basename "$schema_file" .json)
            output_file="$OUTPUT_DIR/$module/${filename}.html"
            echo "    Generating ${filename}.html..."
            
            # Ensure output directory exists
            mkdir -p "$(dirname "$output_file")"
            
            generate-schema-doc \
                --config-file "$CONFIG_FILE" \
                "$schema_file" \
                "$output_file"
        fi
    done
done

echo "Copying CSS and JS files to _static directory..."
if [ -f "$OUTPUT_DIR/base/schema_doc.css" ]; then
    cp "$OUTPUT_DIR/base/schema_doc.css" "$STATIC_DIR/"
    echo "  Copied schema_doc.css"
fi
if [ -f "$OUTPUT_DIR/base/schema_doc.min.js" ]; then
    cp "$OUTPUT_DIR/base/schema_doc.min.js" "$STATIC_DIR/"
    echo "  Copied schema_doc.min.js"
fi

echo "Updating HTML files to reference _static resources and add scoped expand/collapse..."
for html_file in "$OUTPUT_DIR"/*/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file" .html)
        # Replace relative CSS/JS paths with absolute _static paths (portable for Linux and macOS)
        sed_pfx='sed -i'
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed_pfx="sed -i ''"
        else
            echo "Linux is ok"
        fi
        $sed_pfx 's|href="schema_doc.css"|href="_static/schema_doc.css"|g' "$html_file"
        $sed_pfx 's|src="schema_doc.min.js"|src="_static/schema_doc.min.js"|g' "$html_file"
        # Add unique container ID to body tag
        $sed_pfx "s|<body onload=\"anchorOnLoad();\" id=\"root\">|<body onload=\"anchorOnLoad();\" id=\"root\"><div class=\"schema-container\" id=\"schema-${filename}\">|g" "$html_file"
        # Close the container div before closing body tag
        $sed_pfx 's|</body>|</div></body>|g' "$html_file"
        # Update expand/collapse buttons to be scoped to their container
        $sed_pfx "s|data-toggle=\"collapse\" data-target=\".collapse:not(.show)\"|onclick=\"expandAllInContainer('schema-${filename}')\"|g" "$html_file"
        $sed_pfx "s|data-toggle=\"collapse\" data-target=\".collapse.show\"|onclick=\"collapseAllInContainer('schema-${filename}')\"|g" "$html_file"

    fi
done

echo "Removing footer text from HTML files..."
for html_file in "$OUTPUT_DIR"/*/*.html; do
    if [ -f "$html_file" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' '/Generated using.*json-schema-for-humans/d' "$html_file"
        else
            # Linux
            sed -i '/Generated using.*json-schema-for-humans/d' "$html_file"
        fi
    fi
done

echo "Replacing h1 tags with h3 tags..."
for html_file in "$OUTPUT_DIR"/*/*.html; do
    if [ -f "$html_file" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' 's|<h1|<h3|g' "$html_file"
            sed -i '' 's|</h1>|</h3>|g' "$html_file"
        else
            # Linux
            sed -i 's|<h1|<h3|g' "$html_file"
            sed -i 's|</h1>|</h3>|g' "$html_file"
        fi
    fi
done

echo "Injecting custom CSS for font size reduction..."
for html_file in "$OUTPUT_DIR"/*/*.html; do
    if [ -f "$html_file" ]; then
        # Insert link to custom CSS after the schema_doc.css link
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' 's|<link rel="stylesheet" type="text/css" href="_static/schema_doc.css">|<link rel="stylesheet" type="text/css" href="_static/schema_doc.css">\n\t<link rel="stylesheet" type="text/css" href="_static/schema_overrides.css">|g' "$html_file"
        else
            # Linux
            sed -i 's|<link rel="stylesheet" type="text/css" href="_static/schema_doc.css">|<link rel="stylesheet" type="text/css" href="_static/schema_doc.css">\n\t<link rel="stylesheet" type="text/css" href="_static/schema_overrides.css">|g' "$html_file"
        fi
    fi
done

echo "Schema documentation generation complete!"