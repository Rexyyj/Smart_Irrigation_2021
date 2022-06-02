import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ActionComponent } from './pages/action/action.component';
import { ContactComponent } from './pages/contact/contact.component';
import { CropsGrafanaComponent } from './pages/crops/crops-grafana.component';
import { CropsListComponent } from './pages/crops/crops-list.component';
import { InvalidUserComponent } from './pages/login/invalid-user/invalid-user.component';
import { LoginComponent } from './pages/login/login.component';
import { UnauthorizedUserComponent } from './pages/login/unauthorized-user/unauthorized-user.component';
import { LogoutComponent } from './pages/logout/logout.component';
import { ManualAcessComponent } from './pages/manual-acess/manual-acess.component';
import { RegisterComponent } from './pages/register/register.component';
import { WeatherComponent } from './pages/weather/weather.component';

const routes: Routes = [
  { path: 'crops', component: CropsListComponent },
  { path: 'grafana/:cropId', component: CropsGrafanaComponent },
  { path: 'login', component: LoginComponent },
  { path: 'action', component: ActionComponent },
  { path: 'weather', component: WeatherComponent },
  { path: 'invalid', component: InvalidUserComponent },
  { path: 'unauthorized', component: UnauthorizedUserComponent },
  { path: 'manual', component: ManualAcessComponent },
  { path: 'logout', component: LogoutComponent },
  { path: 'contact', component: ContactComponent },
  { path: 'register', component: RegisterComponent },
  { path: '', redirectTo: 'login', pathMatch: 'full' },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
