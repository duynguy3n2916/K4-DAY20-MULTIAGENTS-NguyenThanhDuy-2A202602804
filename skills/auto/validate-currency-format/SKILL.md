---
name: validate-currency-format
description: Use when ensuring monetary values are correctly formatted in cents.
---
1. Convert all monetary values to integer cents (e.g., 1606.67 USD becomes 160667).
2. Validate that no negative values are present unless explicitly allowed (e.g., for missing amounts).
3. Check that all monetary fields are consistently formatted across the dataset.
4. Implement unit tests to verify the currency formatting logic.
5. Document the currency formatting rules in the project guidelines.
