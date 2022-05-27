import { Component, OnInit } from '@angular/core';
import { ICrops } from './crops';
import { CropsService } from '../crops/crop-list-service.service';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import jsonp from 'jsonp';

@Component({
  //selector: 'pm-crops',
  templateUrl: './crops-list.component.html',
  styleUrls: ['./crop-list.component.css'],
})
export class CropsListComponent implements OnInit {
  pageTitle: string = 'Overall information';
  imageWidth: number = 70;
  imageMargin: number = 2;
  showImage: boolean = true;
  showDetails: boolean = false;
  datas: any;
  listIndex = 0;
  isRegister = false;
  locationList = [
    {
      location: 'Grugliasco',
      id: 1,
      img: 'assets/images/123.png',
      modalImgList: [
        'assets/images/NDMI.png',
      ],
    },
    {
      location: 'Torino',
      id: 2,
      img: 'assets/images/satellite.jpg',
      modalImgList: [
        'assets/images/NDMI.png',
      ],
    },
  ];
  private _listFilter: string = '';
  private isAutheticated: boolean = false;
  private roles: string[] = [];
  dataLoaded: boolean = false;
  constructor(
    private cropsService: CropsService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient
  ) { }

  get listFilter(): string {
    return this._listFilter;
  }
  set listFilter(value: string) {
    if (value != '' || value != null) {
      this._listFilter = value;
      console.log('In setter: ', value);
      this.filteredCrops = this.performFilter(value);
    }
  }

  filteredCrops: ICrops[] = [];

  crops: ICrops[] = [];

  performFilter(filterBy: string): ICrops[] {
    filterBy = filterBy.toLocaleLowerCase();
    if (filterBy != '') {
      return this.crops.filter((crops: ICrops) =>
        crops.cropName.toLocaleLowerCase().includes(filterBy)
      );
    } else {
      return this.crops;
    }
  }

  toggleImage(): void {
    this.showDetails = !this.showDetails;
  }

  ngOnInit(): void {
    if (window.sessionStorage.getItem('user')) {
      let data = window.sessionStorage.getItem('user');
      if (typeof data != undefined && typeof data != null && data) {
        let userData = JSON.parse(data);
        this.isAutheticated = userData.isAuthenticated;
        this.roles = userData.roles;
        if (userData.email === 'admin@gmail.com') {
          this.isRegister = true;
        } else {
          this.isRegister = false;
        }
      }
    }
    if (this.isAutheticated) {
      if (this.roles.includes('farmer')) {
        var element = document.getElementById('overlay2');
        if (typeof element != undefined && typeof element != null && element) {
          element.style.display = 'block';
        }
        this.cropsService.getCropsData().subscribe({
          next: (cropsData) => {
            this.crops = cropsData as ICrops[];
            this.filteredCrops = cropsData as ICrops[];
            this.dataLoaded = true;
            if (
              typeof element != undefined &&
              typeof element != null &&
              element
            ) {
              element.style.display = 'none';
            }
          },
          error: (error) => {
            console.error('There was an error!', error);
          },
        });
      } else {
        this.router.navigate([`/unauthorized`], { relativeTo: this.route });
      }
    } else {
      this.router.navigate([`/invalid`], { relativeTo: this.route });
    }
    this.getData();
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
  showImgModal(id: string) {
    const el1 = document.getElementById(id) as any;
    el1.style.display = 'block';
  }
  closeImgModal(id: string) {
    const el1 = document.getElementById(id) as any;
    el1.style.display = 'none';
  }
  getData() {
    this.http
      .get(
        'http://api.weatherapi.com/v1/forecast.json?key=55ab66112c1c47ad97b154807222801&q=Grugliasco&days=3&aqi=no&alerts=no'
      )
      .subscribe(
        (val) => {
          undefined;
          this.datas = val;
          console.log('Post call successful value returned in body', val);
        },
        (error) => {
          undefined;

          console.log('Post call in error', error);
        }
      );
  }
}
