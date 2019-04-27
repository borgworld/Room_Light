# Room_Light

Room Light is a project to count how many people enter a room, and turn the light on when there are people in the room, and off when everybody has left.

The Room Light project is composed of a Raspberry Pi, 2 lasers, 2 light sensors, Trådfri router and bulb (from Ikea) and a Python program.

The 2 lasers are positioned approximately 10 cm apart, and are pointing at the 2 light sensors. So when you cross through the hall or the stairs you will be intercepting the laser light for the 2 light sensors, and the sensors will detect in which direction you are going. If you are going into the room then the light will be turned on. If another person then enters the room, the person count will increase to 2, and the light will stay on. When someone passes the sensors in the other direction, the person count is reduced by 1. Once the person count reaches 0, the light in the room will be turned off.

![Room Light diagram](https://github.com/borgworld/Room_Light/blob/master/RoomLight-diagram.png "Room Light diagram")

### Light sensor board schematic
![Light sensor board schematic](https://github.com/borgworld/Room_Light/blob/master/photos/light_sensor_board.png "Light sensor board schematic")

# Some photos from the project

### Light sensor board
![Light sensor board](https://github.com/borgworld/Room_Light/blob/master/photos/IMG_1519.png "Light sensor board")

### Prototype
![Prototype](https://github.com/borgworld/Room_Light/blob/master/photos/IMG_1556.png "Prototype")

### Laser box step I
![Laser box step I](https://github.com/borgworld/Room_Light/blob/master/photos/IMG_1858.png "Laser box step I")

### Laser box step II
![Laser box step II](https://github.com/borgworld/Room_Light/blob/master/photos/img_1862.png "Laser box step II")

### Laser box mounted
![Laser box mounted](https://github.com/borgworld/Room_Light/blob/master/photos/IMG_1867.png "Laser box mounted")
