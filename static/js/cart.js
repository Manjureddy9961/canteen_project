function printCart() {
    window.print();
}

function removeFromCart(button) {
    const orderId = button.dataset.orderId;
    if (confirm('Are you sure you want to remove this item from the cart?')) {
        fetch('/remove_from_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `order_id=${orderId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Item removed from cart!');
                location.reload(); // Refresh the page to update the cart
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to remove item from cart.');
        });
    }
}