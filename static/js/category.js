$(document).ready(function() {
    // Qidiruv uchun hodisa
    $('#searchInput').on('keyup', function() {
        var query = $(this).val().toLowerCase();
        $('.service-item').each(function() {
            $(this).toggle($(this).data('name').toLowerCase().indexOf(query) > -1);
        });
    });

    // Kategoriya tanlanganida xizmatlar select maydonini yangilash
    $('#categorySelect').on('change', function() {
        var selectedCategory = $(this).val();
        $('#serviceSelect').empty().append('<option value="all">Barchasi</option>');

        if (selectedCategory === 'all') {
            {% for category, services in categories.items %}
                {% for service in services %}
                $('#serviceSelect').append('<option value="{{ service.service }}" data-category="{{ category }}">{{ service.name }}</option>');
                {% endfor %}
            {% endfor %}
        } else {
            {% for category, services in categories.items %}
                if (selectedCategory === "{{ category }}") {
                    {% for service in services %}
                    $('#serviceSelect').append('<option value="{{ service.service }}" data-category="{{ category }}">{{ service.name }}</option>');
                    {% endfor %}
                }
            {% endfor %}
        }
    });

    // Xizmat tavsilotlarini ko'rsatish uchun funksiya
    window.showServiceDetails = function(serviceId) {
        const service = services.find(s => s.service === serviceId);
        if (service) {
            document.getElementById('serviceDescription').textContent = service.description;
            document.getElementById('serviceCompletionTime').textContent = `Tugatish vaqti: ${service.completion_time}`;
            document.getElementById('servicePrice').textContent = service.price;
            $('#serviceDetailModal').modal('show');
        }
    }
});
