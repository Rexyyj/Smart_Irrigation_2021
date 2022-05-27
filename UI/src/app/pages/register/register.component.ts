import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { EndrDecrServiceService } from 'src/app/services/endr-decr-service.service';
import { AuthService } from '../login/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {

  isModel = false;

  loginUserData = {
    email: '',
    email1: '',
    name:'',
    psd:'',
  };

  constructor(
  ) { }

  ngOnInit() {

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
  randId() {
    const c = 'psd' + Math.random();
    return c.replace(/[^0-1a-zA-Z]+/ig, '');
  }
  random(prefix = "", randomLength = 7) {
    // 兼容更低版本的默认值写法
    prefix === undefined ? prefix = "" : prefix;
    randomLength === undefined ? randomLength = 8 : randomLength;

    // 设置随机用户名
    // 用户名随机词典数组
    let nameArr = [
      [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
      ["a", "b", "c", "d", "e", "f", "g", "h", "i", "g", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    ]
    // 随机名字字符串
    let name = prefix;
    // 循环遍历从用户词典中随机抽出一个
    for (var i = 0; i < randomLength; i++) {
      // 随机生成index
      let index = Math.floor(Math.random() * 2);
      let zm = nameArr[index][Math.floor(Math.random() * nameArr[index].length)];
      // 如果随机出的是英文字母
      if (index === 1) {
        // 则百分之50的概率变为大写
        if (Math.floor(Math.random() * 2) === 1) {
          zm = zm.toString().toUpperCase();
        }
      }
      // 拼接进名字变量中
      name += zm;
    }
    // 将随机生成的名字返回
    return name;
  }
  Register(){
    if(this.loginUserData.email == ''||this.loginUserData.email1 == ''){
      alert('Please enter the email');
      return;
    }
    if(this.loginUserData.email != this.loginUserData.email1 ){
      alert('The two emails are inconsistent');
      return;
    }
    console.log(this.randId(),this.random('SG'))
    this.loginUserData.psd = this.randId();
    this.loginUserData.name = this.random('SG');
    this.isModel = true;
  }
  close(){
    this.loginUserData.psd = '';
    this.loginUserData.name = '';
    this.isModel = false;
  }
}
