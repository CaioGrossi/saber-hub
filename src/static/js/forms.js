function setupCollegeFieldToggle() {
    const collegeSelects = document.querySelectorAll('select[name="college_choice"]');

    collegeSelects.forEach((collegeSelect) => {
        const form = collegeSelect.closest('form');
        if (!form) {
            return;
        }

        const collegeInput = form.querySelector('input[name="college"]');
        const collegeField = form.querySelector('[data-college-name-field]');

        if (!collegeInput || !collegeField) {
            return;
        }

        const toggleCollegeField = () => {
            const shouldHide = collegeSelect.value === 'no_college';

            collegeField.classList.toggle('is-hidden', shouldHide);
            collegeInput.disabled = shouldHide;

            if (shouldHide) {
                collegeInput.value = '';
            }
        };

        collegeSelect.addEventListener('change', toggleCollegeField);
        toggleCollegeField();
    });
}

document.addEventListener('DOMContentLoaded', setupCollegeFieldToggle);
