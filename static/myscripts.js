import { Grid } from "https://unpkg.com/gridjs?module";

const initGrid = () =>{
    const grid = new Grid({
    // Grid configuration options
    columns: [
        { id: 'region', name: 'Region' },
        { id: 'city', name: 'City' },
        { id: 'suburb', name: 'Suburb', sort: false },
        { id: 'ptype', name: 'Property Type', sort: false },
        { id: 'askpx', name: 'Asking Price'},
        { id: 'area', name: 'Area'},
    ],
    data: [],
    search: {
        selector: (cell, rowIndex, cellIndex) => [0, 1, 4].includes(cellIndex) ? cell : null,
    },
    sort: true,
    pagination: true,
    plugins: {
    multiFilter: true,
        }
    }).render(document.getElementById("table"));

    // Event listener for the "Apply Filters" button
    document.getElementById("applyFilters").addEventListener("click", async () => {
        const region = document.getElementById("regionFilter").value;
        const city = document.getElementById("cityFilter").value;
        // Collect more filter values as needed

        const url = `/filter-listings?region=${region}&city=${city}`;
        // Add more filter parameters to the URL

        const response = await fetch(url);
        const data = await response.json();
        grid.update(data.data);
    });
};

export default initGrid;





// $(document).ready(function() {
//     $('#todo-section, #progress-section, #done-section, #overdue-section, #archived-section').hide();

//     $('#cardtodo').click(function() {
//         $('.cardTag').not(this).removeClass('card-bigger');
//         $('.btn-outline-info').not(this).removeClass('active');
//         $(this).toggleClass('card-bigger');
//         $('#todo-section').show();
//         $('#default-section').hide();
//         $('#progress-section').hide();
//         $('#done-section').hide();
//         $('#overdue-section').hide();
//         $('#archived-section').hide();
//     });

//     $('#carddoing').click(function() {
//         $('.cardTag').not(this).removeClass('card-bigger');
//         $('.btn-outline-info').not(this).removeClass('active');
//         $(this).toggleClass('card-bigger');
//         $('#todo-section').hide();
//         $('#default-section').hide();
//         $('#progress-section').show();
//         $('#done-section').hide();
//         $('#overdue-section').hide();
//         $('#archived-section').hide();
//     });

//     $('#carddone').click(function() {
//         $('.cardTag').not(this).removeClass('card-bigger');
//         $('.btn-outline-info').not(this).removeClass('active');
//         $(this).toggleClass('card-bigger');
//         $('#todo-section').hide();
//         $('#default-section').hide();
//         $('#progress-section').hide();
//         $('#done-section').show();
//         $('#overdue-section').hide();
//         $('#archived-section').hide();
//     });

//     $('#cardoverdue').click(function() {
//         $('.cardTag').not(this).removeClass('card-bigger');
//         $('.btn-outline-info').not(this).removeClass('active');
//         $(this).toggleClass('card-bigger');
//         $('#todo-section').hide();
//         $('#default-section').hide();
//         $('#progress-section').hide();
//         $('#done-section').hide();
//         $('#overdue-section').show();
//         $('#archived-section').hide();
//     });

//     $('#archived-btn').click(function() {
//         $('.cardTag').not(this).removeClass('card-bigger');
//         $('.btn-outline-info').not(this).removeClass('active');
//         $(this).toggleClass('active');
//         $('#todo-section').hide();
//         $('#default-section').hide();
//         $('#progress-section').hide();
//         $('#done-section').hide();
//         $('#overdue-section').hide();
//         $('#archived-section').show();
//     });
  
// });



//     // $('#todo-section, #progress-section, #done-section, #overdue-section, #archived-section').hide();
//     // function revealFunction(id) {
//     //   $('#' + id).show();
//     //   btn.classList.toggle('highlight');

// //       var defaults = document.getElementById("default-section");
// //       var todo = document.getElementById("todo-section");
// //       var progress = document.getElementById("progress-section");
// //       var done = document.getElementById("done-section");
// //       var overdue = document.getElementById("overdue-section");
// //       var archived = document.getElementById("archived-section");

// //     //  const button1 = document.getElementById('todo-btn');
// //     //  const button2 = document.getElementById('doing-btn');
// //     //  const button3 = document.getElementById('done-btn');
// //     //  const button4 = document.getElementById('overdue-btn');

// //         document.getElementById(id).style.display = 'block';
// //         // hide the lorem ipsum text
// //         if (btn == "defaults"){
// //             progress.style.display = 'none';
// //             todo.style.display = 'none';
// //             done.style.display = 'none';
// //             overdue.style.display = 'none';
// //             archived.style.display = 'none';
// //         }

// //         if (btn == "todo"){
// //             $('todo-section').show();
// //             defaults.style.display = 'none';
// //             progress.style.display = 'none';
// //             done.style.display = 'none';
// //             overdue.style.display = 'none';
// //             archived.style.display = 'none';
// //         }
// //         else if (btn == "done"){
// //             defaults.style.display = 'none';
// //             progress.style.display = 'none';
// //             todo.style.display = 'none';
// //             overdue.style.display = 'none';
// //             archived.style.display = 'none';
// //         }
// //         else if (btn == "progress"){
// //             defaults.style.display = 'none';
// //             todo.style.display = 'none';
// //             done.style.display = 'none';
// //             overdue.style.display = 'none';
// //             archived.style.display = 'none';
// //         }
// //         else if (btn == "overdue"){
// //             defaults.style.display = 'none';
// //             progress.style.display = 'none';
// //             done.style.display = 'none';
// //             todo.style.display = 'none';
// //             archived.style.display = 'none';
// //         }
// //         else if (btn == "archived"){
// //             defaults.style.display = 'none';
// //             progress.style.display = 'none';
// //             done.style.display = 'none';
// //             todo.style.display = 'none';
// //             overdue.style.display = 'none';
// //         }
// //         else{
// //         console.log("smth else is clicked")
// //         }

// //     }
// // });
