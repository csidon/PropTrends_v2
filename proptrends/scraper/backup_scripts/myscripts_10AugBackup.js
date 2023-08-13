import { Grid, html } from "https://unpkg.com/gridjs?module";

$(document).ready(function() {
  $('#suburbSelect').select2({
    placeholder: 'Select suburbs...',
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

    const suburbSelect = document.getElementById('suburbSelect');
    console.log('hiiiii')
    // Add event listener using select2's change event
    $('#suburbSelect').on('change', async function() {
      const selectedSuburbs = $(this).val();
      selectedSuburbs.sort();
      console.log(selectedSuburbs);

      const url = `/filter-and-sort?suburbs=${selectedSuburbs.join(',')}`;
      const response = await fetch(url);
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
