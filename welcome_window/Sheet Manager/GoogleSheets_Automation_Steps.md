# Google Sheets Automation: EOD Data Archival Process

## Overview
This document describes the process and requirements for automating the end-of-day (EOD) archival of technician activity data from the "Daily Activity" sheet to the "ALL Work" sheet in a Google Sheets workbook. The process is designed to ensure that all technician work is logged, archived by week, and easily accessible for reporting and auditing.

---

## Sheet Structure

- **Daily Activity Sheet**: Contains technician work logs for the current day. User data starts at row 5. Each technician has 5 columns: `User`, `Date`, `Time`, `SKU`, `Tracking`.
- **ALL Work Sheet**: Archives all technician work, divided into weekly sections. Each new week, columns are duplicated to the right, shifting previous weeks for archival.
- **Steps❗️ Sheet**: Used for scripting and automation steps.

---

## Manual EOD Process (Current)
1. Go to the "Daily Activity" sheet.
2. Select cell F5 (the start of the 1st user data).
3. Press `Ctrl+Shift+Down Arrow` to select all rows for the day in that column.
4. Press `Ctrl+Shift+Left Arrow` to select all columns for those rows, covering all user data for the day.
5. Copy the selection.
6. Go to the "ALL Work" sheet.
7. Paste the data into the section for the current week.
8. At the start of each new week, duplicate the columns for a new week, shifting previous weeks to the right.

---

## Automation Goals
- **Automate Data Selection**: Script should programmatically select all relevant user data starting from the user's fifth cell (First user F5), covering all rows and columns for the day.
- **Automate Data Copying**: Script should copy the selected data and append/paste it into the correct week in the "ALL Work" sheet.
- **Weekly Archival**: At the start of each week, script should duplicate the current week's columns to the right, creating a new section for the new week.

---

## Google Sheets Script Function Example Current State

A function for the "Steps❗️" sheet to select the data as described:

```javascript
function selectUserData() {
  var sheet = SpreadsheetApp.getActive().getSheetByName('Steps❗️');
  var startCell = sheet.getRange('F5');
  var lastRow = sheet.getLastRow();
  var lastCol = startCell.getColumn();
  // Find the last column with data in row 5
  while (sheet.getRange(5, lastCol + 1).getValue() !== '') {
    lastCol++;
  }
  // Select the range from F5 to the last filled cell in the data block
  var dataRange = sheet.getRange(5, 6, lastRow - 4, lastCol - 5);
  SpreadsheetApp.setActiveRange(dataRange);
}
```

---

## Next Steps
- Create a new Apps Script deployment, I'm not sure what yo use. (Web App, API Executable, Library)
- Integate this deployment for future updating thtough the Python APP Sheets Manager.
- Integrate this function into your Google Sheets via Apps Script.	//NOT SURE ABOUT THIS
- Expand the script to automate copying and pasting data into the "ALL Work" sheet, and handle weekly archival.
- Optionally, trigger the script on a schedule (e.g., every day at EOD) or via a custom menu/button.

---

## Notes
- Adjust column and row indices as needed based on your actual sheet structure.
- Ensure you have appropriate permissions to run and authorize Google Apps Scripts on your sheet.
