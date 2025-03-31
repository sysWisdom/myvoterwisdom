import wixData from 'wix-data';

$w.onReady(function () {
    console.log("Page is ready");
    
    // Load unique states into the state dropdown
    wixData.query("countyDataset")
        .ascending("state")
        .distinct("state")
        .then((results) => {
            console.log("States fetched:", results.items);
            const states = results.items.map(item => item.State);
            $w("#dropdownState").options = states.map(state => {
                return { label: state, value: state };
            });
        });

    // Set up an event handler for when a state is selected
    $w("#dropdownState").onChange((event) => {
        const selectedState = event.target.value;
        console.log("Selected state:", selectedState);

        // Query the counties in the selected state
        wixData.query("Import835")
            .eq("state", selectedState)
            .ascending("county")
            .limit(1)
            .find()
            .then((results) => {
                console.log("Counties fetched for state:", results.items);

                if (results.items.length > 0) {
                   const counties = results.items.map(item => item.county);
                   $w("#countyDropDown").options = counties.map(county => {
                       return { label: county, value: county };
                   });
                   $w("#countyDropDown").enable(); // Enable the dropdown after filtering
                } else {
                    console.log("No counties found for the selected state");
                    $w("#countyDropDown").options = []; // Clear options if no results
                    $w("#countyDropDown").disable();
                }  
        })
        .catch((error) => {
            console.error("Error querying counties:", error);
        });
    });
    
    // Disable the county dropdown initially
    $w("#countyDropDown").disable();

});
