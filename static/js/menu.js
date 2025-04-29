document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.category h2').forEach(header => {
        header.addEventListener('click', () => {
            const items = header.nextElementSibling;
            items.style.display = items.style.display === 'block' ? 'none' : 'block';
            header.querySelector('.arrow').textContent = items.style.display === 'block' ? '▲' : '▼';
        });
    });

    document.querySelectorAll('.add-btn').forEach(button => {
        button.addEventListener('click', () => {
            const itemId = button.dataset.id;
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `item_id=${itemId}&quantity=1`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Item added to cart!');
                } else {
                    alert(data.error);
                }
            });
        });
    });
});