import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ActionComponent } from './pages/action/action.component';
import { CropsGrafanaComponent } from './pages/crops/crops-grafana.component';
import { CropsListComponent } from './pages/crops/crops-list.component';
import { HomeComponent } from './pages/home/home.component';
import { AuthService } from './pages/login/auth.service';
import { InvalidUserComponent } from './pages/login/invalid-user/invalid-user.component';
import { LoginComponent } from './pages/login/login.component';
import { UnauthorizedUserComponent } from './pages/login/unauthorized-user/unauthorized-user.component';
import { ManualAcessComponent } from './pages/manual-acess/manual-acess.component';
import { WeatherComponent } from './pages/weather/weather.component';
import { EndrDecrServiceService } from './services/endr-decr-service.service';
import { ContactComponent } from './pages/contact/contact.component';
import { RegisterComponent } from './pages/register/register.component';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    LoginComponent,
    CropsListComponent,
    CropsGrafanaComponent,
    LoginComponent,
    ActionComponent,
    InvalidUserComponent,
    UnauthorizedUserComponent,
    WeatherComponent,
    ManualAcessComponent,
    ContactComponent,
    RegisterComponent,
  ],
  imports: [BrowserModule, AppRoutingModule, FormsModule, HttpClientModule],
  providers: [EndrDecrServiceService, AuthService],
  bootstrap: [AppComponent],
})
export class AppModule {}
