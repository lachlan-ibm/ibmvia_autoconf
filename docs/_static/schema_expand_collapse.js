// Scoped expand/collapse functions for schema documentation
// These functions allow expand/collapse buttons to only affect their respective schema sections

function expandAllInContainer(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        $(container).find(".collapse:not(.show)").collapse("show");
    }
}

function collapseAllInContainer(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        $(container).find(".collapse.show").collapse("hide");
    }
}

// Initialize all embedded schema sections when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Find all schema containers
    const schemaContainers = document.querySelectorAll('.schema-container');
    
    // Call anchorOnLoad for each container if the function exists
    if (typeof anchorOnLoad === 'function') {
        schemaContainers.forEach(function(container) {
            // Set the context to this container and call anchorOnLoad
            anchorOnLoad();
        });
    }
});

// Made with Bob
