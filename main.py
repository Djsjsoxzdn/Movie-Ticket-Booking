import json
import os
import random
from datetime import datetime

# ─────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────

MOVIES = {
    "1": {
        "title": "Interstellar",
        "showtimes": ["10:00 AM", "1:00 PM", "4:00 PM", "7:00 PM"],
        "available_seats": {"10:00 AM": 50, "1:00 PM": 50, "4:00 PM": 50, "7:00 PM": 50},
        "price": 180,
    },
    "2": {
        "title": "KGF Chapter 2",
        "showtimes": ["11:00 AM", "2:00 PM", "5:00 PM", "9:00 PM"],
        "available_seats": {"11:00 AM": 50, "2:00 PM": 50, "5:00 PM": 50, "9:00 PM": 50},
        "price": 200,
    },
    "3": {
        "title": "RRR",
        "showtimes": ["9:30 AM", "12:30 PM", "3:30 PM", "6:30 PM"],
        "available_seats": {"9:30 AM": 50, "12:30 PM": 50, "3:30 PM": 50, "6:30 PM": 50},
        "price": 160,
    },
    "4": {
        "title": "Oppenheimer",
        "showtimes": ["10:30 AM", "2:30 PM", "6:00 PM", "9:30 PM"],
        "available_seats": {"10:30 AM": 50, "2:30 PM": 50, "6:00 PM": 50, "9:30 PM": 50},
        "price": 220,
    },
}

BOOKINGS_FILE = "bookings.json"

# ─────────────────────────────────────────
#  FILE HANDLING
# ─────────────────────────────────────────

def load_bookings():
    """Load bookings from JSON file. Returns empty list if file not found."""
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, "r") as f:
                data = json.load(f)
                # Also restore seat counts from saved bookings
                for booking in data["bookings"]:
                    movie_id = booking["movie_id"]
                    showtime = booking["showtime"]
                    seats = booking["seats"]
                    if movie_id in MOVIES and showtime in MOVIES[movie_id]["available_seats"]:
                        MOVIES[movie_id]["available_seats"][showtime] -= seats
                return data["bookings"]
        except (json.JSONDecodeError, KeyError):
            print("Warning: bookings file is corrupted. Starting fresh.\n")
    return []


def save_bookings(bookings):
    """Save all bookings to JSON file."""
    with open(BOOKINGS_FILE, "w") as f:
        json.dump({"bookings": bookings}, f, indent=4)


# ─────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────

def divider(char="─", width=55):
    print(char * width)


def header(text):
    divider("═")
    print(f"  {text}")
    divider("═")


def display_movies():
    """Print all available movies with showtimes and seat availability."""
    header("🎬  AVAILABLE MOVIES")
    for movie_id, info in MOVIES.items():
        print(f"\n  [{movie_id}] {info['title']}  |  ₹{info['price']} per seat")
        divider("─", 55)
        for showtime in info["showtimes"]:
            seats = info["available_seats"][showtime]
            status = "✅" if seats > 0 else "❌ HOUSEFUL"
            print(f"       {showtime:<12}  Seats available: {seats}  {status}")
    print()


# ─────────────────────────────────────────
#  CORE FEATURES
# ─────────────────────────────────────────

def book_ticket(bookings):
    """Book a ticket: pick movie → showtime → seats → confirm."""
    header("🎟️  BOOK A TICKET")
    display_movies()

    # Select movie
    movie_id = input("Enter movie number (or 0 to go back): ").strip()
    if movie_id == "0":
        return
    if movie_id not in MOVIES:
        print("❌ Invalid movie number. Please try again.\n")
        return

    movie = MOVIES[movie_id]
    print(f"\nYou selected: {movie['title']}")
    divider()

    # Select showtime
    print("Available showtimes:")
    for i, showtime in enumerate(movie["showtimes"], 1):
        seats = movie["available_seats"][showtime]
        status = f"({seats} seats left)" if seats > 0 else "(HOUSEFUL)"
        print(f"  {i}. {showtime}  {status}")

    try:
        st_choice = int(input("\nEnter showtime number (or 0 to go back): ").strip())
    except ValueError:
        print("❌ Please enter a valid number.\n")
        return

    if st_choice == 0:
        return
    if st_choice < 1 or st_choice > len(movie["showtimes"]):
        print("❌ Invalid showtime. Please try again.\n")
        return

    showtime = movie["showtimes"][st_choice - 1]
    available = movie["available_seats"][showtime]

    if available == 0:
        print("❌ Sorry, this show is houseful!\n")
        return

    # Number of seats
    try:
        seats = int(input(f"\nHow many seats? (Max: {available}): ").strip())
    except ValueError:
        print("❌ Please enter a valid number.\n")
        return

    if seats <= 0:
        print("❌ Number of seats must be at least 1.\n")
        return
    if seats > available:
        print(f"❌ Only {available} seats available for this show.\n")
        return

    # Confirmation
    total = seats * movie["price"]
    print(f"\n{'─'*55}")
    print(f"  Movie    : {movie['title']}")
    print(f"  Showtime : {showtime}")
    print(f"  Seats    : {seats}")
    print(f"  Total    : ₹{total}")
    print(f"{'─'*55}")
    confirm = input("Confirm booking? (y/n): ").strip().lower()

    if confirm != "y":
        print("Booking cancelled.\n")
        return

    # Create booking
    booking_id = f"BK{random.randint(10000, 99999)}"
    booking = {
        "booking_id": booking_id,
        "movie_id": movie_id,
        "movie": movie["title"],
        "showtime": showtime,
        "seats": seats,
        "total": total,
        "booked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    bookings.append(booking)
    movie["available_seats"][showtime] -= seats
    save_bookings(bookings)

    print(f"\n✅ Booking Confirmed!")
    print(f"   Your Booking ID: {booking_id}")
    print(f"   Please note it for cancellation.\n")


def cancel_ticket(bookings):
    """Cancel a booking by Booking ID."""
    header("❌  CANCEL TICKET")

    if not bookings:
        print("No bookings found to cancel.\n")
        return

    booking_id = input("Enter your Booking ID (e.g. BK12345): ").strip().upper()

    # Find booking
    found = None
    for b in bookings:
        if b["booking_id"] == booking_id:
            found = b
            break

    if not found:
        print(f"❌ No booking found with ID: {booking_id}\n")
        return

    print(f"\n  Booking ID : {found['booking_id']}")
    print(f"  Movie      : {found['movie']}")
    print(f"  Showtime   : {found['showtime']}")
    print(f"  Seats      : {found['seats']}")
    print(f"  Total Paid : ₹{found['total']}")

    confirm = input("\nAre you sure you want to cancel? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancellation aborted.\n")
        return

    # Restore seats
    movie_id = found["movie_id"]
    showtime = found["showtime"]
    MOVIES[movie_id]["available_seats"][showtime] += found["seats"]

    bookings.remove(found)
    save_bookings(bookings)
    print(f"\n✅ Booking {booking_id} cancelled successfully.\n")


def view_bookings(bookings):
    """Display all current bookings."""
    header("📋  MY BOOKINGS")

    if not bookings:
        print("No bookings found.\n")
        return

    for b in bookings:
        print(f"\n  Booking ID : {b['booking_id']}")
        print(f"  Movie      : {b['movie']}")
        print(f"  Showtime   : {b['showtime']}")
        print(f"  Seats      : {b['seats']}")
        print(f"  Total      : ₹{b['total']}")
        print(f"  Booked At  : {b['booked_at']}")
        divider("─")

    print()


# ─────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────

def main():
    bookings = load_bookings()

    print("\n" + "═" * 55)
    print("       🎬  MOVIE TICKET BOOKING SYSTEM  🎬")
    print("              Alliance University")
    print("═" * 55)

    while True:
        print("\n  MAIN MENU")
        divider()
        print("  1. View Movies & Showtimes")
        print("  2. Book a Ticket")
        print("  3. Cancel a Ticket")
        print("  4. View My Bookings")
        print("  5. Exit")
        divider()

        choice = input("  Enter your choice (1-5): ").strip()

        if choice == "1":
            display_movies()
        elif choice == "2":
            book_ticket(bookings)
        elif choice == "3":
            cancel_ticket(bookings)
        elif choice == "4":
            view_bookings(bookings)
        elif choice == "5":
            print("\n👋 Thank you for using the Movie Ticket Booking System!")
            print("   Goodbye!\n")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 5.\n")


if __name__ == "__main__":
    main()
