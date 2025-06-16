from tkinter import *
import tkinter as tk
from geopy.geocoders import Nominatim
from tkinter import ttk, messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
import csv
import os

def get_Weather():
    try:
        error_label.config(text="")  
        city= textfield.get()
        geolocator = Nominatim(user_agent="weather_app_arif")
        location= geolocator.geocode(city)
        obj= TimezoneFinder()
        result= obj.timezone_at(lng=location.longitude, lat=location.latitude)

        home= pytz.timezone(result)
        local_time= datetime.now(home)
        current_time= local_time.strftime("%I:%M %p")
        clock.config(text=current_time)
        name.config(text="Current Weather")
        
        # Taiwan time
        taiwan_zone = pytz.timezone("Asia/Taipei")
        taiwan_now = datetime.now(taiwan_zone)
        taiwan_now_str = taiwan_now.strftime("%I:%M %p")
        taiwan_time.config(text=taiwan_now_str)

        #weather api
        api= "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid=c9b6f2153ac173c06b006ef4b8a9720a"
        json_data= requests.get(api).json()
        condition= json_data["weather"][0]["main"]
        description= json_data["weather"][0]["description"]
        temp= int(json_data["main"]["temp"]-273.15)
        pressure= (json_data["main"]["pressure"])
        humidity= (json_data["main"]["humidity"])
        wind= (json_data["wind"]["speed"]* 3.6 )
    
        t.config(text=(temp, "°C"))
        c.config(text=(condition, "|", "Feels", "Like", temp, "°C"))
        w.config(text=f"{wind:.1f} km/h") 
        h.config(text=f'{humidity} %')
        d.config(text=description)
        p.config(text=f'{pressure} mbar')

    except Exception as e:
        show_error()

def show_error():
    reset_output()
    error_label.config(text="Invalid City\nPlease enter a valid city name!")

def save_weather():
    if t.cget("text") == "...":
        messagebox.showinfo("No Data", "Please search for a city first.")
        return
    
    try:
        city = textfield.get()
        temperature = t.cget("text")
        condition_text = c.cget("text")
        wind_speed = w.cget("text")
        humidity = h.cget("text")
        description = d.cget("text")
        pressure = p.cget("text")
        time_fetched = clock.cget("text")

        folder = "Data Weather Report"
        if not os.path.exists(folder):
            os.makedirs(folder)

        file_path = os.path.join(folder, "weather_data.csv")
        file_exists = os.path.isfile(file_path)

        # Open CSV file in append mode
        with open(file_path, "a", newline="") as csvfile:
            fieldnames = ["City", "Time", "Temperature", "Condition", "Wind", "Humidity", "Description", "Pressure"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)


            if not file_exists:
                writer.writeheader()

            writer.writerow({
                "City": city,
                "Time": time_fetched,
                "Temperature": temperature,
                "Condition": condition_text,
                "Wind": wind_speed,
                "Humidity": humidity,
                "Description": description,
                "Pressure": pressure
            })

        messagebox.showinfo("Success", f"Weather data saved to {file_path}!")
        print(f"Weather data saved to: {os.path.abspath(file_path)}")


    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data:\n{e}")

def reset_output():
    # clock.config(text="")
    name.config(text="")
    t.config(text="")
    c.config(text="")
    w.config(text="...")
    h.config(text="...")
    d.config(text="...")
    p.config(text="...")
    error_label.config(text="")

#initiate GUI
root = Tk()
root.title("GUI for Weather app")
root.geometry("900x500+300+200")
root.resizable(False, False)

search_img = PhotoImage(file="S:/Asia University Code/Mid_Term/Advance_programing/Copy of search.png")
myimg= Label(image=search_img)
myimg.place(x=20, y=20)

textfield= tk.Entry(root, justify="center", width=17, font=("poppins",25, "bold"), bg="#404040", border=0, fg="white")
textfield.place(x=50, y=40)
textfield.focus()

search_icon= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\Copy of search_icon.png")
myimg_icon= Label(image=search_icon, borderwidth= 0, cursor="hand2", bg="#404040")
myimg_icon.place(x=400, y=34)
myimg_icon.bind("<Button-1>", lambda event: get_Weather())

#logo
logo_img= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\Copy of logo.png")
logo= Label(image=logo_img)
logo.place(x=150, y=100)

#bottom box
frame_img= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\Copy of box.png")
frame_myimg= Label(image=frame_img)
frame_myimg.pack(padx=5,pady=5, side=BOTTOM)

#time
name= Label(root, font=("Helvetica", 15,"bold"))
name.place(x=30,y=100)
clock= Label(root, font=("Helvetica", 20,"bold"))
clock.place(x=30, y=130)

# Taiwan Time
taiwan_label = Label(root, font=("Helvetica", 15, "bold"), text="Taiwan Time")
taiwan_label.place(x=30, y=170)

taiwan_time = Label(root, font=("Helvetica", 20, "bold"))
taiwan_time.place(x=30, y=200)


#label
label1= Label(root, text="Wind", font=("Helvetica",15,"bold"),fg="white",bg="#1ab5ef")
label1.place(x= 120, y=400)
w_icon= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\wind1.png")
w_icon_label= Label(image=w_icon, bg="#00AEEF")
w_icon_label.image = w_icon
w_icon_label.place(x= 95, y=403)

label2= Label(root, text="Humidity", font=("Helvetica",15,"bold"),fg="white",bg="#1ab5ef")
label2.place(x= 250, y=400)
h_icon= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\humidity1.png")
h_icon_label= Label(image=h_icon, bg="#00AEEF")
h_icon_label.image = h_icon
h_icon_label.place(x= 225, y=403)

label3= Label(root, text="Description", font=("Helvetica",15,"bold"),fg="white",bg="#1ab5ef")
label3.place(x= 430, y=400)
d_icon= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\info1.png")
d_icon_label= Label(image=d_icon, bg="#00AEEF")
d_icon_label.image = d_icon
d_icon_label.place(x= 405, y=403)

label4= Label(root, text="Pressure", font=("Helvetica",15,"bold"),fg="white",bg="#1ab5ef")
label4.place(x= 650, y=400)
p_icon= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\pressure1.png")
p_icon_label= Label(image=p_icon, bg="#00AEEF")
p_icon_label.image = p_icon
p_icon_label.place(x= 625, y=403)

t= Label(font=("Helvetica", 70,"bold"), fg="#ee666d")
t.place(x=400, y=150)
c= Label(font=("Helvetica", 15,"bold"))
c.place(x=400, y=250)

w= Label(text="...",font=("Helvetica",20,"bold"), bg="#1ab5ef")
w.place(x=120, y=430)
h= Label(text="...",font=("Helvetica",20,"bold"), bg="#1ab5ef")
h.place(x=280, y=430)
d= Label(text="...",font=("Helvetica",20,"bold"), bg="#1ab5ef")
d.place(x=380, y=430)
p= Label(text="...",font=("Helvetica",20,"bold"), bg="#1ab5ef")
p.place(x=660, y=430)

error_label = tk.Label(
    root,
    justify="left",
    text="",
    fg="red",
    font=("Helvetica", 20, "bold") 
)
error_label.place(x=400, y=150)  

# save_button = Button(root, text="Save Weather", font=("Helvetica", 12, "bold"), bg="#1ab5ef", fg="white", command=save_weather)
# save_button.place(x=750, y=40)

save_icon= PhotoImage(file="S:\Asia University Code\Mid_Term\Advance_programing\save-file.png")
mysave_icon= Label(image=save_icon, borderwidth= 0, cursor="hand2")
mysave_icon.place(x=750, y=30)
mysave_icon.bind("<Button-1>", lambda event: save_weather())

root.mainloop() 