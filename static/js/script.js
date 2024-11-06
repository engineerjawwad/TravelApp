
document.querySelector("form").addEventListener("submit", (event) => {
    event.preventDefault();
    const destination = event.target[0].value;
    const departureDate = new Date(event.target[1].value);
    const returnDate = new Date(event.target[2].value);

    if (departureDate >= returnDate) {
        alert("Return date must be after departure date.");
    } else {
        alert(`Searching for options to ${destination} from ${departureDate.toDateString()} to ${returnDate.toDateString()}`);
        
        const booking = {
            destination,
            departureDate: departureDate.toDateString(),
            returnDate: returnDate.toDateString()
        };
        localStorage.setItem("lastBooking", JSON.stringify(booking));
    }
});