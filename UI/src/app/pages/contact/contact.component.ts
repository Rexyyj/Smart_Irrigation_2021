import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CropsService } from '../crops/crop-list-service.service';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent implements OnInit {

  constructor(
    private cropsService: CropsService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
  }
  openNav() {
    const el1 = document.getElementById('mySidebar') as any;
    const el2 = document.getElementById('main') as any;
    if (el1) {
      el1.style.width = '250px';
    }
    if (el2) {
      el2.style.marginLeft = '250px';
    }
  }

  /* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
  closeNav() {
    const el1 = document.getElementById('mySidebar') as any;
    const el2 = document.getElementById('main') as any;
    if (el1) {
      el1.style.width = '0';
    }
    if (el2) {
      el2.style.marginLeft = '0';
    }
  }
}
