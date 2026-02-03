<script>
    document.addEventListener('DOMContentLoaded', function() {

        // 1. Track Contact Form Submissions
        document.addEventListener('wpcf7mailsent', function (event) {
            if (typeof gtag === 'function') {
                gtag('event', 'generate_lead', {
                    'event_category': 'Contact Form',
                    'event_label': 'Submission'
                });
            }
        }, false);

    // 2. Track PDF Downloads
    var pdfLinks = document.querySelectorAll('a[href$=".pdf"]');
    pdfLinks.forEach(function(link) {
        link.addEventListener('click', function () {
            if (typeof gtag === 'function') {
                gtag('event', 'file_download', {
                    'event_category': 'PDF',
                    'event_label': link.href.split('/').pop()
                });
            }
        });
    });

    // 3. Track Phone Number Clicks
    var phoneLinks = document.querySelectorAll('a[href^="tel:"]');
    phoneLinks.forEach(function(link) {
        link.addEventListener('click', function () {
            if (typeof gtag === 'function') {
                gtag('event', 'click_phone', {
                    'event_category': 'Contact',
                    'event_label': link.href.replace('tel:', '')
                });
            }
        });
    });

    // 4. Track Email Clicks
    var emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    emailLinks.forEach(function(link) {
        link.addEventListener('click', function () {
            if (typeof gtag === 'function') {
                gtag('event', 'click_email', {
                    'event_category': 'Contact',
                    'event_label': link.href.replace('mailto:', '')
                });
            }
        });
    });

    // 5. Track "Buy Online" Clicks
    var buyButtons = document.querySelectorAll('.aec-buy-btn');
    buyButtons.forEach(function(btn) {
        btn.addEventListener('click', function () {
            if (typeof gtag === 'function') {
                gtag('event', 'click_buy_online', {
                    'event_category': 'Outbound',
                    'event_label': 'Google Search'
                });
            }
        });
    });

});
</script>
