# Ticket Booking App

A modern, interactive ticket booking application built with FastAPI, HTML, CSS, and JavaScript. Book tickets for movies, trains, and flights with a beautiful, themeable interface.

## Features

- 🎬 **Movie Ticket Booking** - Book tickets for your favorite movies
- 🚂 **Train Ticket Booking** - Reserve train tickets for your journey
- ✈️ **Flight Ticket Booking** - Book flight tickets to your destination
- 🌓 **Light/Dark Theme** - Toggle between light and dark themes with a single click
- 🎨 **Distinct Color Themes** - Each booking type has its own unique color scheme:
  - Movies: Purple/Blue theme
  - Trains: Green/Teal theme
  - Flights: Orange/Red theme
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
FWD project/
├── main.py                 # FastAPI backend application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html         # Home page
│   ├── movies.html        # Movie booking page
│   ├── trains.html        # Train booking page
│   └── flights.html       # Flight booking page
└── static/                # Static files (CSS, JS)
    ├── style.css          # Main stylesheet with themes
    ├── script.js          # Theme switcher functionality
    ├── movies.js          # Movie booking form handler
    ├── trains.js          # Train booking form handler
    └── flights.js         # Flight booking form handler
```

## Usage

1. **Home Page**: Navigate to the home page to see all booking options
2. **Theme Switcher**: Click the theme button (🌙/☀️) in the top-left corner to toggle between light and dark themes
3. **Book Tickets**: Click on any booking option (Movies, Trains, or Flights) to access the booking form
4. **Submit Booking**: Fill out the form and submit to book your tickets

## API Endpoints

- `GET /` - Home page
- `GET /movies` - Movie booking page
- `GET /trains` - Train booking page
- `GET /flights` - Flight booking page
- `POST /api/book/movie` - Book a movie ticket
- `POST /api/book/train` - Book a train ticket
- `POST /api/book/flight` - Book a flight ticket
- `GET /api/bookings/{booking_type}` - Get all bookings for a type

## Theme Customization

The app uses CSS variables for easy theme customization. Each booking type has its own color scheme defined in `static/style.css`. The theme preference is saved in localStorage and persists across page reloads.

## Technologies Used

- **Backend**: NodeJsw
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: CSS Variables, Flexbox, CSS Grid
- **Server**: Uvicorn

## License

This project is open source and available for educational purposes.

