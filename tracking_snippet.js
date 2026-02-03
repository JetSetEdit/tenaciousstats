<script>
document.addEventListener( 'wpcf7mailsent', function( event ) {
    // This listens for the successful submission of the Contact Form
    if ( typeof gtag === 'function' ) {
        gtag('event', 'generate_lead', {
            'event_category': 'Contact Form',
            'event_label': 'Submission',
            'value': 50 // Optional: Assign a value to the lead (e.g., $50)
        });
        console.log('GA4 Lead Event Sent');
    }
}, false );
</script>
