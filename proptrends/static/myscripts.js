import { Grid, html } from "https://unpkg.com/gridjs?module";

$(document).ready(function() {
  console.log('Document is now ready');
  $('select[name="suburb_to_scrape"] option[value="Auckland"]').prop('disabled', true);

  $('#suburbSelect').select2({
    placeholder: 'Select suburbs to filter by...',
  });

  $('#proptypeSelect').select2({
    placeholder: 'Select property types to filter by...',
  });

  // Manually trigger form submission
  $('#run-script-button').on('click', function(event) {
    event.preventDefault(); // Prevent default form submission
    $('#scraping-form').submit(); // Manually submit the form
  });

  const initGrid = () =>{
      return new Grid({
        // Grid configuration options
        columns: [
            { id: 'city', name: 'City' },
            { id: 'address', name: 'Address' },
            { id: 'suburb', name: 'Suburb', sort: true },
            { id: 'prop_type', name: 'Property Type', sort: true },
            { id: 'list_price', name: 'Asking Price'},
            { id: 'floor_m2', name: 'Area'},
            { id: 'psqm', name: '$/sqm'},
            { id: 'compare_img', name: 'Compare $/sqm',
                                  formatter: (cell) => html(renderImage(cell))
                                  },
        ],
        data: listingsData,
        sort: true,
        // pagination: true,
        resizable: true
      

      }).render(document.getElementById("table"));
      console.log('I render okay here')
    };

    // Create the initial Grid.js table
    const grid = initGrid();

    const proptypeSelect = document.getElementById('proptypeSelect');
    const suburbSelect = document.getElementById('suburbSelect');
    console.log('hiiiii')
    // Add event listener using select2's change event
    $('#suburbSelect, #proptypeSelect').on('change', async function() {
      const selectedFilter = {
        suburbs: $('#suburbSelect').val(),
        prop_type: $('#proptypeSelect').val(),
      }
      
      console.log(selectedFilter);
      const suburbPropType = selectedFilter.suburbs.map(suburb_name => encodeURIComponent(suburb_name));
      const encodedPropType = selectedFilter.prop_type.map(type => encodeURIComponent(type));
      const url = `/filter-and-sort?suburbs=${suburbPropType.join(',')}&prop_type=${encodedPropType.join(',')}`;


      // const allFilters = `suburbs=${selectedFilter.suburbs.join(',')}&prop_type=${selectedFilter.prop_type.join(',')}`;
      // const url = `/filter-and-sort?${allFilters}`
      // const url = `/filter-and-sort?${$.param(selectedFilter)}`;
      const response = await fetch(url);
      console.log('Do I has response? : ', response)
      const newData = await response.json();

      console.log('i is logging', newData)
      // Transforming newData from a list of dictionaries to a list of lists
      const newDataList = newData.listings.map(listing => [
        listing.city,
        listing.address,
        listing.suburb,
        listing.prop_type,
        listing.list_price,
        listing.floor_m2,
        listing.psqm,
        listing.compare_img,
      ]);

      // Clear and update the Grid.js table with the received data
      grid.updateConfig({
        data: newDataList,
      }).forceRender();

      // Update avg_listing_price_psqm
      
      const avgListingPricePsqmElement = document.getElementById('avg-listing-price-psqm');
      avgListingPricePsqmElement.textContent = newData.avg_listing_price_psqm;
      console.log("The avg listing psqm is...! :", avgListingPricePsqmElement)
    });

});
// renderImageTest("3.png")
// function renderImageTest(imageName){
//   const imageURL = `./images/${imageName}`
//   const imgElement = document.createElement('img');
//   imgElement.src = imageUrl;
//   imgElement.alt = imageName;
//   imgElement.width = 200; // Adjust the image width if needed
//   imgElement.height = 150; // Adjust the image height if needed
//   const imageContainer = document.getElementById('imageContainer');
//   imageContainer.appendChild(imgElement);
// }

  

// renderImage("5.png")
// Custom formatter function for displaying images
function renderImage(cell) {
  const imageName = cell;
  const imageURL = `../static/images/${imageName}`;
  const imageHTML = `<img src="${imageURL}" alt="${imageName}" width="100" height="100">`;
  return imageHTML;
}

          // suburbSelect.addEventListener('change', async () => {
    //   console.log('hello?')
    //   const selectedSuburbs = Array.from(suburbSelect.selectedOptions, option => option.value);
    //   console.log(selectedSuburbs)

    //   const url = `/filter-and-sort?suburbs=${selectedSuburbs.join(',')}`;
    //   const response = await fetch(url);
    //   const data = await response.json();

    //   // Clear and update the Grid.js table with the received data
    //   grid.update(data.data);

      // // Event listener for the "Apply Filters" button
      // document.getElementById("applyFilters").addEventListener("click", async () => {
      //     const region = document.getElementById("regionFilter").value;
      //     const city = document.getElementById("cityFilter").value;
      //     const suburb = document.getElementById("suburbFilter").value;
      //     // Collect more filter values as needed

      //     const url = `/filter-listings?region=${region}&city=${city}&suburb=${suburb}`;
      //     // Add more filter parameters to the URL

      //     const response = await fetch(url);
      //     const data = await response.json();
      //     grid.update(data.data);
      // });


  // // Calling initGrid function immediately
  // initGrid();
