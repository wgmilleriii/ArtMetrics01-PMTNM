# NM AG Portal Web Scraping Exploration

## Goal

Determine if we can automate financial data extraction from the NM Attorney General Charity Registry portal instead of relying on manual PDF downloads.

## Portal URL Pattern

```
https://secure.nmag.gov/CharitySearch/CharityDetail.aspx?FEIN={9-digit-EIN}
```

Example: `https://secure.nmag.gov/CharitySearch/CharityDetail.aspx?FEIN=850284938` (PMTNM)

## Findings

### ✅ Portal is Reachable
- No Cloudflare blocking or anti-bot protection
- HTTP 200 response, standard HTML content
- Can fetch with normal User-Agent headers

### ❌ Portal Does Not Display Financial Data
- Web interface shows: "There are no financials that can be reviewed in Charity Search at this time"
- Portal displays only: registration status, org metadata (name, FEIN, address)
- Actual financial metrics are PDF-only

### ❌ Portal Uses ASP.NET ViewState
- Server-side state management (`__VIEWSTATE` hidden input)
- PDF download links require form submission + ViewState handling
- Not directly accessible via URL pattern alone

### ❌ No Direct PDF Download Link
- Portal does not expose direct PDF URLs
- PDF access requires: search → navigate to org → click download (multi-step form submission)
- Would require Selenium/Playwright to automate (brings back the headless browser problem)

## Implication

**Web scraping approach is NOT practical for this data source.**

The portal is a registration/search interface, not a data API. To get PDFs via scraping would require:
1. Simulating form submissions (complex ASP.NET ViewState handling)
2. Headless browser automation (Selenium/Playwright)
3. Anti-bot workarounds (delays, proxies for 50-state scale)

This creates the same friction we wanted to avoid by not automating PDF downloads.

## Recommendation

**Stick with current approach: Manual PDF download + Automated Parsing**

### Why This is Better

1. **Simpler pipeline**: You download, we parse (clear separation of concerns)
2. **More reliable**: No risk of portal blocking/changing API
3. **Already proven**: Parser successfully handles 12 PMTNM files (2014-2024)
4. **Better data quality**: Direct from original source, not via portal's limited search

### For 50-State Expansion

Each state AG registry will have different:
- Data structure (some use portals, some use HTML forms, some expose CSVs)
- Anti-bot policies
- PDF formatting

**Strategy for scale:**
- Evaluate each state's registry individually (some might be scrapeable)
- Build per-state adapters (not a one-size-fits-all approach)
- Prioritize states with easiest data access first (direct file downloads, APIs, or public datasets)
- Use manual download + automated parsing as fallback

### Alternative: Contact NM AG

Could request bulk export of charity registration data from NM AG directly:
- Email: charity.registrar@nmag.gov
- Might have CSV export or API access for legitimate research requests
- Worth trying, especially for 50-state expansion

## Conclusion

**Current approach (manual PDF + automated parser) is optimal for NM scale.**

For national scale, a mixed strategy:
- Some states: automated scraping
- Some states: bulk data requests
- Some states: manual download (fallback)
- Parser adapts to each state's PDF format variations

The real value is in **parser scalability** (handling format variations), not in **download automation**.
