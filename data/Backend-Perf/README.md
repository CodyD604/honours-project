* "NewMethod" refers to the "Hash and Tally Method" which had an issue where all received audit events would be converted to objects even if this wasn't necessary, hurting performance. This wasn't reported on as it wasn't a very interesting fix.
* "NewMethodImproved" refers to the "Hash and Tally Method" approach referred to in the final report.
* "OldMethod" refers to the "Save Immediately" approach referred to in the final report.
* RawSteps contains the relevant console output containing our data for trials with 1 through 4 producer threads for each method.