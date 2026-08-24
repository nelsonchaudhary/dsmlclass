from vehicles import Bike, Car
from decorators import ride_logger
from exceptions import DistanceError


@ride_logger
def book(vehicle, distance):
    fare = vehicle.calculate_fare(distance)

    print("Driver:", vehicle.driver)
    print("Vehicle:", vehicle.__class__.__name__)
    print("Distance:", distance, "km")
    print("Fare: Rs.", fare)

    try:
        file = open("ride_history.txt", "a")
        file.write(vehicle.driver + " ")
        file.write(vehicle.__class__.__name__ + " ")
        file.write(str(distance) + " ")
        file.write(str(fare) + "\n")
        file.close()
    except:
        print("File Error")


try:
    v = input("Enter Vehicle Type (Bike/Car): ")
    name = input("Enter Driver Name: ")
    rating = float(input("Enter Rating: "))
    distance = float(input("Enter Distance: "))

    if distance < 0:
        raise DistanceError("Distance cannot be negative")

    if v.lower() == "bike":
        vehicle = Bike(name)
    elif v.lower() == "car":
        vehicle = Car(name)
    else:
        print("Invalid Vehicle")
        exit()

    vehicle.rating = rating

    book(vehicle, distance)

except ValueError as e:
    print(e)

except DistanceError as e:
    print(e)