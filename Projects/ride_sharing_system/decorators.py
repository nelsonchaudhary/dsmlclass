def ride_logger(func):
    def wrapper(*args):
        print("\nRide booked successfully!")
        return func(*args)
    return wrapper