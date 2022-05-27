import { Component, OnInit } from '@angular/core';
import { mqttInit, publishMessage } from 'src/utils/mqtt';
@Component({
  selector: 'app-manual-acess',
  templateUrl: './manual-acess.component.html',
  styleUrls: ['./manual-acess.component.css'],
})
export class ManualAcessComponent implements OnInit {
  checkList = [
    { ischeck: false, ischeckNum: 0 },
    { ischeck: false, ischeckNum: 0 },
    { ischeck: false, ischeckNum: 0 },
    { ischeck: false, ischeckNum: 0 },
    { ischeck: false, ischeckNum: 0 },
  ];
  constructor() {}

  ngOnInit(): void {
    mqttInit();
  }

  check(i: any) {
    //if (this.checkList[i].ischeckNum > 0) {
    this.checkList[i].ischeck = !this.checkList[i].ischeck;
    if (this.checkList[i].ischeck) {
      // publish mqtt message
      publishMessage('{"downlinks":[{"f_port": 15,"frm_payload":payload_raw,"priority": "NORMAL"}]}');
    }
    //}
  }
  change(type: string, i: number) {
    if (type === '+') {
      this.checkList[i].ischeckNum++;
    }
    if (type === '-' && this.checkList[i].ischeckNum > 0) {
      this.checkList[i].ischeckNum--;
    }
  }
}
