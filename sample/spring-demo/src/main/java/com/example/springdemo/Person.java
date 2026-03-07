package com.example.springdemo;

import java.time.LocalDate;

public class Person {
    private String name;
    private String gender;
    private LocalDate birthdate;
    private String remarks;

    public Person(String name, String gender, LocalDate birthdate, String remarks) {
        this.name = name;
        this.gender = gender;
        this.birthdate = birthdate;
        this.remarks = remarks;
    }

    // Getters and Setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    public LocalDate getBirthdate() { return birthdate; }
    public void setBirthdate(LocalDate birthdate) { this.birthdate = birthdate; }
    public String getRemarks() { return remarks; }
    public void setRemarks(String remarks) { this.remarks = remarks; }
}
