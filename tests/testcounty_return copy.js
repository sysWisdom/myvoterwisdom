import wixData from 'wix-data';
import wixLocationFrontend from 'wix-location-frontend';

$w.onReady(function () {
    console.log("Page is ready");

    // Load unique states into the state dropdown
    wixData.query("countyDataset") // Replace with your actual collection name
        .ascending("state") // Ensure the sorting field matches your collection's field names
        .distinct("state")
        .then((results) => {
            console.log("States fetched:", results.items);
            const states = results.items.map(item => item.state);
            $w("#dropdownState").options = states.map(state => {
                return { label: state, value: state };
            });
        });

    // Disable county dropdown and Go button initially
    $w("#countyDropDown").disable();
    $w("#goBut").disable();

    // Event handler for when a state is selected
    $w("#dropdownState").onChange(() => {
        const selectedState = $w("#dropdownState").value;

        if (selectedState) {
            console.log("Selected state:", selectedState);

            // Query to get counties for the selected state
            wixData.query("Import835") // Replace with your actual collection name
                .eq("state", selectedState) // Filter by selected state
                .ascending("county") // Sort counties alphabetically
                .limit(1)
                .find()
                .then((results) => {
                    console.log("Counties fetched for state:", results.items);

                    if (results.items.length > 0) {
                        const counties = results.items.map(item => item.county);
                        $w("#countyDropDown").options = counties.map(county => {
                            return { label: county, value: county };
                        });
                        $w("#countyDropDown").enable(); // Enable the dropdown after populating
                    } else {
                        console.log("No counties found for the selected state");
                        $w("#countyDropDown").options = []; // Clear options if no results
                        $w("#countyDropDown").disable();
                        $w("#goBut").disable();
                    }
                })
                .catch((error) => {
                    console.error("Error querying counties:", error);
                });
        } else {
            console.log("No state selected");
            $w("#countyDropDown").options = []; // Clear options if no state is selected
            $w("#countyDropDown").disable();
            $w("#goBut").disable();
        }
    });

    // Event handler for when a county is selected
    $w("#countyDropDown").onChange(() => {
        const selectedCounty = $w("#countyDropDown").value;

        if (selectedCounty) {
            console.log("Selected county:", selectedCounty);
            $w("#goBut").enable(); // Enable the Go button only after a county is selected
        } else {
            console.log("No county selected");
            $w("#goBut").disable();
        }
    });

    // Event handler for the Go button
    $w("#goBut").onClick(() => {
        const selectedState = $w("#dropdownState").value;
        const selectedCounty = $w("#countyDropDown").value;

        if (selectedState && selectedCounty) {
            console.log(`Applying filter for State: ${selectedState}, County: ${selectedCounty}`);
            
            // Query your collection based on selected state and county
            wixData.query("Import835") // Replace with your actual collection name
                .eq("state", selectedState)
                .eq("county", selectedCounty)
                .find()
                .then((results) => {
                    console.log("Filtered results:", results.items);

                    // Apply the results to a repeater, table, or other element
                    $w("#repeater5").data = results.items; // Example for using a repeater

                    // Preserve dropdown selections
                    $w("#dropdownState").value = selectedState;
                    $w("#countyDropDown").value = selectedCounty;
                })
                .catch((error) => {
                    console.error("Error applying filter:", error);
                });
        } else {
            console.log("State or county not selected. Filter not applied.");
        }
    });
    // New function to handle predictionButton click
    $w('#predictionButton').onClick(() => {
        const state = $w('#stateDropdown').value;
        const county = $w('#countyDropdown').value;
    
        if (state && county) {
            const dynamicPageUrl = `/voting-county/${state}/${county}`;
            wixLocationFrontend.to(dynamicPageUrl);
        }
    });  
});