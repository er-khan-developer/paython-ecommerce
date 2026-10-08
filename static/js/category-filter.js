const productsGrid = document.getElementById('products-grid');
const productsCount = document.getElementById('products-count');
const categoryLabel = document.getElementById('category-label');
const filterData = document.getElementById('category-filter-data');
const filterUrl = filterData.dataset.filterUrl;
const clearFilterButton = document.getElementById('clear-category-filter');

let activeCategoryId = '';
let activeSubcategoryId = '';

function setLoadingState(isLoading) {
    productsGrid.setAttribute('aria-busy', String(isLoading));
    productsGrid.style.opacity = isLoading ? '0.55' : '1';
}

async function filterProducts(categoryId = '', subcategoryId = '') {
    const params = new URLSearchParams();

    if (categoryId) {
        params.set('category_id', categoryId);
    }
    if (subcategoryId) {
        params.set('subcategory_id', subcategoryId);
    }

    activeCategoryId = categoryId;
    activeSubcategoryId = subcategoryId;
    setLoadingState(true);

    try {
        const response = await fetch(`${filterUrl}?${params.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error('Unable to load products');
        }

        const data = await response.json();
        productsGrid.innerHTML = data.products_html;
        productsCount.textContent = `${data.products_count} products shown`;
        categoryLabel.textContent = data.category_label === 'All Categories'
            ? 'Our Products'
            : `${data.category_label} Products`;

        document.querySelectorAll('[data-subcategory-id]').forEach((button) => {
            const isSelected = button.dataset.subcategoryId === subcategoryId;
            button.classList.toggle('btn-primary', isSelected);
            button.classList.toggle('btn-outline-dark', !isSelected);
            button.setAttribute('aria-pressed', String(isSelected));
        });

        clearFilterButton.hidden = !categoryId && !subcategoryId;
    } catch (error) {
        console.error(error);
        productsGrid.innerHTML = '<div class="col-12 alert alert-danger">Unable to load products. Please try again.</div>';
    } finally {
        setLoadingState(false);
    }
}

document.querySelectorAll('[data-subcategory-id]').forEach((button) => {
    button.addEventListener('click', () => {
        filterProducts(button.dataset.categoryId, button.dataset.subcategoryId);
    });
});

clearFilterButton.addEventListener('click', () => {
    document.querySelectorAll('[data-subcategory-id]').forEach((button) => {
        button.classList.add('btn-outline-dark');
        button.classList.remove('btn-primary');
        button.setAttribute('aria-pressed', 'false');
    });
    filterProducts();
});

window.addEventListener('DOMContentLoaded', () => {
    if (activeCategoryId || activeSubcategoryId) {
        filterProducts(activeCategoryId, activeSubcategoryId);
    }
});
