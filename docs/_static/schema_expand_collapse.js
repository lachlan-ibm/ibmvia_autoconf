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

// Made with Bob
