function updateCart(itemId, action) {
    // Action ke hisaab se URL decide karein
    let ajaxUrl = '';
    if (action === 'increase') ajaxUrl = `/cart/increase/${itemId}/`;
    if (action === 'decrease') ajaxUrl = `/cart/decrease/${itemId}/`;
    if (action === 'remove') ajaxUrl = `/cart/remove/${itemId}/`;

    // jQuery AJAX call
    $.ajax({
        url: ajaxUrl,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                $('#nav-cart-count').text(response.cart_count);
                
                // Cart ka overall Total amount update karein
                $('#cart-total').text('₹ ' + response.cart_total);

                // Agar action remove ka tha ya item ki quantity 0 hoke delete ho gaya hai
                if (action === 'remove' || response.is_deleted) {
                    // FadeOut effect ke sath row hata dega, smooth UX ke liye
                    $(`#item-row-${itemId}`).fadeOut(300, function() {
                        $(this).remove();
                        
                        // Agar cart ki value 0 ho gayi, toh page reload karein taaki empty message dikhe
                        if (response.cart_total == 0) {
                            window.location.reload();
                        }
                    });
                } else {
                    // Nayi quantity aur price text me set karein
                    $(`#qty-${itemId}`).text(response.quantity);
                    $(`#item-total-${itemId}`).text('₹ ' + response.item_total);
                }
            }
        },
        error: function(xhr, status, error) {
            console.error("AJAX Error: ", error);
            alert("Kuch galat ho gaya, kripya page refresh karein.");
        }
    });
}


function addProductToCart(productId, btnElement) {
    $.ajax({
        url: `/cart/add-to-cart/${productId}/`,
        type: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Backend ko batane ke liye ki ye AJAX hai
        },
        success: function(response) {
            if (response.success) {
                // 1. Navbar badge update karein
                $('#nav-cart-count').text(response.cart_count);
                
                // 2. Button ka text aur color change karein as feedback
                let originalText = $(btnElement).text();
                $(btnElement).text('Added! ✓').removeClass('btn-warning').addClass('btn-success text-white');
                
                // 3. 2 seconds ke baad button wapas normal kar dein
                setTimeout(() => {
                    $(btnElement).text(originalText).removeClass('btn-success text-white').addClass('btn-warning');
                }, 2000);
            }
        },
        error: function() {
            // Agar user logged in nahi hai toh Login page par bhej dein
           // window.location.href = '/login/';
        }
    });
}