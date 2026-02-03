# Google Business Profile API Access Form - Filling Guide

Use this guide to complete the Google Business Profile API access request form.

## Form Fields & Answers

### 1. What is your name? *
**Answer:** `Tenacious Tapes`

### 2. Email address *
**Answer:** `customerservice@tenacioustapes.com.au`
- Use an email from the same domain as your company website
- This will be used for communications about your API access

### 3. Which email addresses will administer the Project ID? *
**Answer:** `tenacioustapesmedia@gmail.com`
- Or whatever Google account you use to access Google Cloud Platform
- You can list multiple emails separated by commas if needed

### 4. Company Name *
**Answer:** `Tenacious Tapes`

### 5. Company Website *
**Answer:** `https://www.tenacioustapes.com.au`

### 6. Google Cloud Platform Project ID *
**Answer:** `tenacious-tapes-videos`
- This is found in your service account key file

### 7. Google Cloud Platform Project Number *
**Answer:** `422791924330`
- This is found in the error messages from the test script
- You can also find it in Google Cloud Console: https://console.cloud.google.com/iam-admin/settings?project=tenacious-tapes-videos

### 8. Company HQ's Google Maps Listing URL *
**Answer:** 
- Go to Google Maps and search for "Tenacious Tapes"
- Find your business listing
- Copy the URL from the address bar
- Example format: `https://www.google.com/maps/place/Tenacious+Tapes/...`

**To find it:**
1. Go to https://www.google.com/maps
2. Search for "Tenacious Tapes"
3. Click on your business listing
4. Copy the full URL from the address bar

### 9. In which regions are your merchants/customers located? *
**Select:** `Australia` (and any other regions where you have customers)

### 10. How would you best categorize your company? *
**Select:** Choose the most appropriate category, likely:
- "Manufacturing" or
- "Wholesale/Retail" or
- "Industrial Supplies"

### 11. Why do you need access to the Business Profile APIs? *
**Select:** `Local Insights analytics and reporting`
- This is the primary use case for your dashboard

**Additional context (you can add in a note if there's a text field):**
"We need access to programmatically retrieve Business Profile insights (views, searches, actions) and reviews data to integrate into our internal analytics dashboard for business intelligence and reporting purposes."

### 12. Approximately how many Business Profile locations do you manage today? *
**Answer:** `1` (or however many locations you have)
- If you only have one location, enter `1`

### 13. Please confirm that you have read and agree to the Business Profile APIs policies. *
**Select:** `Yes` ✓

## Important Notes

1. **Sign in first:** Make sure you're signed in to the Google Account associated with your Business Profile before submitting

2. **Project Number Verification:**
   - You can verify the project number by running:
     ```bash
     gcloud projects describe tenacious-tapes-videos --format="value(projectNumber)"
     ```
   - Or check in Google Cloud Console

3. **Google Maps URL:**
   - Make sure you use the exact URL from your verified Business Profile listing
   - This helps Google verify your business

4. **Response Time:**
   - Google typically responds within a few business days
   - They may ask for additional information

5. **After Submission:**
   - Google will contact you at the email address you provided
   - Keep an eye on your inbox (and spam folder)
   - You may need to provide additional documentation

## Quick Checklist Before Submitting

- [ ] Signed in to Google Account associated with Business Profile
- [ ] All required fields filled out
- [ ] Project ID and Project Number verified
- [ ] Google Maps listing URL copied correctly
- [ ] Email address matches company domain
- [ ] Read and agreed to policies

---

**After you submit, you'll need to wait for Google's approval before the API quota is increased.**





