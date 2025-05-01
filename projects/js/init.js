window.onload = function () {
    loadProjects();

    ['tag', 'context', 'type'].forEach(group => {
        const buttons = document.querySelectorAll(`button[data-group="${group}"]:not(.select-all)`);
        buttons.forEach(btn => {
            selected[group].add(btn.textContent.trim());
            btn.classList.add('active');
        });

        const selectAllBtns = document.querySelectorAll(`.select-all[data-group="${group}"]`);
        const regularButtons = document.querySelectorAll(`button[data-group="${group}"]:not(.select-all)`);
        const allSelected = regularButtons.length > 0 &&
            selected[group].size === regularButtons.length;

        selectAllBtns.forEach(btn => {
            btn.textContent = allSelected ? 'Deselect All' : 'Select All';
            btn.classList.toggle('active', allSelected);
        });
    });

    filterProjects();
};
