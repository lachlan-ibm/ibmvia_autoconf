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

echo "Copying CSS files to _static directory..."
if [ -f "$OUTPUT_DIR/base/schema_doc.css" ]; then
    cp "$OUTPUT_DIR/base/schema_doc.css" "$STATIC_DIR/"
    echo "  Copied schema_doc.css"
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
        fi
        # Match both quoted and unquoted href/src attributes in minified HTML
        $sed_pfx 's|href=schema_doc\.css|href=_static/schema_doc.css|g' "$html_file"
        $sed_pfx 's|href="schema_doc\.css"|href="_static/schema_doc.css"|g' "$html_file"
        $sed_pfx 's|src=schema_doc\.min\.js|src=_static/schema_doc.min.js|g' "$html_file"
        $sed_pfx 's|src="schema_doc\.min\.js"|src="_static/schema_doc.min.js"|g' "$html_file"
        # Add unique container ID to body tag
        $sed_pfx "s|<body onload=\"anchorOnLoad();\" id=\"root\">|<body onload=\"anchorOnLoad();\" id=\"root\"><div class=\"schema-container\" id=\"schema-${filename}\">|g" "$html_file"
        # Also handle minified version without quotes
        $sed_pfx "s|<body onload=anchorOnLoad(); id=root>|<body onload=anchorOnLoad(); id=root><div class=\"schema-container\" id=\"schema-${filename}\">|g" "$html_file"
        # Close the container div before closing body tag
        $sed_pfx 's|</body>|</div></body>|g' "$html_file"
        # Update expand/collapse buttons to be scoped to their container
        # Match the actual minified HTML patterns with and without quotes
        $sed_pfx "s|data-toggle=\"collapse\" data-target=\"\.collapse:not(\.show)\"|onclick=\"expandAllInContainer('schema-${filename}')\"|g" "$html_file"
        $sed_pfx "s|data-toggle=\"collapse\" data-target=\"\.collapse\.show\"|onclick=\"collapseAllInContainer('schema-${filename}')\"|g" "$html_file"
        $sed_pfx "s|data-toggle=collapse data-target=\.collapse:not(\.show)|onclick=\"expandAllInContainer('schema-${filename}')\"|g" "$html_file"
        $sed_pfx "s|data-toggle=collapse data-target=\.collapse\.show|onclick=\"collapseAllInContainer('schema-${filename}')\"|g" "$html_file"
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
            # macOS - handle both minified and regular HTML
            sed -i '' 's|href=_static/schema_doc\.css>|href=_static/schema_doc.css><link rel=stylesheet type=text/css href=_static/schema_overrides.css>|g' "$html_file"
            sed -i '' 's|href="_static/schema_doc\.css">|href="_static/schema_doc.css"><link rel="stylesheet" type="text/css" href="_static/schema_overrides.css">|g' "$html_file"
        else
            # Linux - handle both minified and regular HTML
            sed -i 's|href=_static/schema_doc\.css>|href=_static/schema_doc.css><link rel=stylesheet type=text/css href=_static/schema_overrides.css>|g' "$html_file"
            sed -i 's|href="_static/schema_doc\.css">|href="_static/schema_doc.css"><link rel="stylesheet" type="text/css" href="_static/schema_overrides.css">|g' "$html_file"
        fi
    fi
done

echo "Stripping HTML/head/body wrappers from schema files for proper embedding..."
for html_file in "$OUTPUT_DIR"/*/*.html; do
    if [ -f "$html_file" ]; then
        # Extract only the body content (everything between <body> and </body>)
        # This removes the opening body tag and everything before it, and the closing body/html tags
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' 's/^.*<body[^>]*>//g' "$html_file"
            sed -i '' 's/<\/body>.*$//g' "$html_file"
            # Remove the extra closing div that was added before </body>
            sed -i '' 's|</div>$||g' "$html_file"
        else
            # Linux
            sed -i 's/^.*<body[^>]*>//g' "$html_file"
            sed -i 's/<\/body>.*$//g' "$html_file"
            # Remove the extra closing div that was added before </body>
            sed -i 's|</div>$||g' "$html_file"
        fi
    fi
done

echo "Schema documentation generation complete!"