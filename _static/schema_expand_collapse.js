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
    // Fix missing heading IDs for Sphinx navigation
    // Find all headerlinks and add the corresponding ID to their parent heading
    document.querySelectorAll('a.headerlink').forEach(function(link) {
        var href = link.getAttribute('href');
        if (href && href.startsWith('#')) {
            var id = href.substring(1); // Remove the '#'
            var heading = link.parentElement;
            if (heading && !heading.id) {
                heading.id = id;
            }
        }
    });
    
    // Process anchor on page load if the function exists
    if (typeof anchorOnLoad === 'function') {
        anchorOnLoad();
    }
});

// Made with Bob
