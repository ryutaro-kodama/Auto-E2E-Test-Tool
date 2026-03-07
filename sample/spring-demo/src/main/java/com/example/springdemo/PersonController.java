package com.example.springdemo;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Controller
public class PersonController {

    private final List<Person> mockData = new ArrayList<>();

    public PersonController() {
        mockData.add(new Person("山田 太郎", "男性", LocalDate.of(1990, 1, 15), "営業部"));
        mockData.add(new Person("佐藤 花子", "女性", LocalDate.of(1995, 5, 20), "人事部"));
        mockData.add(new Person("鈴木 一郎", "男性", LocalDate.of(1985, 11, 3), "開発部マネージャー"));
        mockData.add(new Person("田中 裕子", "女性", LocalDate.of(1992, 8, 12), "広報部"));
        mockData.add(new Person("伊藤 健太", "男性", LocalDate.of(1998, 3, 25), "新人"));
    }

    @GetMapping("/")
    public String listPeople(
            @RequestParam(name = "name", required = false) String name,
            @RequestParam(name = "gender", required = false) String gender,
            @RequestParam(name = "birthdate", required = false) String birthdate,
            @RequestParam(name = "remarks", required = false) String remarks,
            Model model) {
        
        List<Person> filteredData = mockData;
        
        if (name != null && !name.trim().isEmpty()) {
            filteredData = filteredData.stream()
                .filter(p -> p.getName() != null && p.getName().toLowerCase().contains(name.toLowerCase()))
                .collect(Collectors.toList());
        }
        if (gender != null && !gender.trim().isEmpty()) {
            filteredData = filteredData.stream()
                .filter(p -> p.getGender() != null && p.getGender().equals(gender))
                .collect(Collectors.toList());
        }
        if (birthdate != null && !birthdate.trim().isEmpty()) {
            filteredData = filteredData.stream()
                .filter(p -> p.getBirthdate() != null && p.getBirthdate().toString().equals(birthdate))
                .collect(Collectors.toList());
        }
        if (remarks != null && !remarks.trim().isEmpty()) {
            filteredData = filteredData.stream()
                .filter(p -> p.getRemarks() != null && p.getRemarks().toLowerCase().contains(remarks.toLowerCase()))
                .collect(Collectors.toList());
        }

        model.addAttribute("people", filteredData);
        model.addAttribute("name", name);
        model.addAttribute("gender", gender);
        model.addAttribute("birthdate", birthdate);
        model.addAttribute("remarks", remarks);
        
        boolean isSearchActive = (name != null && !name.isEmpty()) || 
                                 (gender != null && !gender.isEmpty()) || 
                                 (birthdate != null && !birthdate.isEmpty()) || 
                                 (remarks != null && !remarks.isEmpty());
        model.addAttribute("isSearchActive", isSearchActive);
        
        return "list";
    }
}
