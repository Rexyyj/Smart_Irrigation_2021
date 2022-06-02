import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualAcessComponent } from './manual-acess.component';

describe('ManualAcessComponent', () => {
  let component: ManualAcessComponent;
  let fixture: ComponentFixture<ManualAcessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ManualAcessComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ManualAcessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
