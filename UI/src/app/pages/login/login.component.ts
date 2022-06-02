import { AuthService } from './auth.service';
import { Component, OnInit } from '@angular/core';
import { EndrDecrServiceService } from '../../services/endr-decr-service.service';
import { Router, ActivatedRoute } from '@angular/router';
import { invalid } from '@angular/compiler/src/render3/view/util';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent implements OnInit {
  //pageTitle: string = 'Login Page';

  private key = '123456$#@$^@1ERF';
  private user: any = {};
  errorMessage = '';
  loginUserData = {
    email: 'farmer@abc.com',
    password: '123456',
  };
  constructor(
    private _auth: AuthService,
    private _encdr: EndrDecrServiceService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    if (window.sessionStorage.getItem('user')) {
      this.router.navigate([`/crops`], { relativeTo: this.route });
    }
  }

  loginUser() {
    if (
      typeof this.loginUserData.email != 'undefined' &&
      this.loginUserData.email &&
      typeof this.loginUserData.password != 'undefined' &&
      this.loginUserData.password
    ) {
      this.loginSuccess({
        id: 1,
        email: this.loginUserData.email,
        roles: 'farmer',
      });
      return;

      // normal
      let data = {
        password: this._encdr.set(this.key, this.loginUserData.password),
        email: this.loginUserData.email,
      };
      this._auth.loginUser(JSON.stringify(data)).subscribe({
        next: (data) => {
          if (data != '0') {
            this.loginSuccess(data);
          } else {
            this.errorMessage = 'Invalid email/password';
            console.error('There was an error!', 'Invalid email/password');
          }
        },
        error: (error) => {
          this.errorMessage = error.message;
          console.error('There was an error!', error);
        },
      });
    }
  }
  loginSuccess(rxdata: any) {
    this.user.id = rxdata.id;
    this.user.email = rxdata.email;
    this.user.roles = rxdata.roles.split(',');
    this.user.isAuthenticated = true;
    window.sessionStorage.setItem('user', JSON.stringify(this.user));
    this.errorMessage = '';
    this.router.navigate([`/crops`], { relativeTo: this.route });
  }
}
