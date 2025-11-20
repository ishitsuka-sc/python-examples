int main()

{
  int c1;
  long in_FS_OFFSET;
  char check;
  undefined8 ret;
  undefined1 buf [104];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  while( true ) {
    puts("What\'s your name?");
    printf("> ");
    ret = read(0,buf,0x200);
    if (buf[ret + -1] == '\n') {
      buf[ret + -1] = 0;
    }
    printf("Your input is %s\n",buf);
    puts("Is this okay (Y/n) ?");
    printf("> ");
    c1 = getchar();
    check = (char)c1;
    if (check == 'Y') break;
    while (check != '\n') {
      c1 = getchar();
      check = (char)c1;
    }
  }
  printf("Hello %s!\n",buf);
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}

void FUN_00101229(void)

{
  long in_FS_OFFSET;
  undefined2 local_a8 [4];
  undefined2 *local_a0;
  undefined2 local_98;
  undefined1 local_96;
  undefined1 local_95;
  undefined4 local_94;
  undefined2 local_90;
  undefined1 local_8e;
  undefined1 local_8d;
  undefined4 local_8c;
  undefined2 local_88;
  undefined1 local_86;
  undefined1 local_85;
  undefined4 local_84;
  undefined2 ret;
  undefined1 local_7e;
  undefined1 local_7d;
  undefined4 local_7c;
  undefined2 buf;
  undefined1 local_76;
  undefined1 local_75;
  undefined4 local_74;
  undefined2 local_70;
  undefined1 local_6e;
  undefined1 local_6d;
  undefined4 local_6c;
  undefined2 local_68;
  undefined1 local_66;
  undefined1 local_65;
  undefined4 local_64;
  undefined2 local_60;
  undefined1 local_5e;
  undefined1 local_5d;
  undefined4 local_5c;
  undefined2 local_58;
  undefined1 local_56;
  undefined1 local_55;
  undefined4 local_54;
  undefined2 local_50;
  undefined1 local_4e;
  undefined1 local_4d;
  undefined4 local_4c;
  undefined2 local_48;
  undefined1 local_46;
  undefined1 local_45;
  undefined4 local_44;
  undefined2 local_40;
  undefined1 local_3e;
  undefined1 local_3d;
  undefined4 local_3c;
  undefined2 local_38;
  undefined1 local_36;
  undefined1 local_35;
  undefined4 local_34;
  undefined2 local_30;
  undefined1 local_2e;
  undefined1 local_2d;
  undefined4 local_2c;
  undefined2 local_28;
  undefined1 local_26;
  undefined1 local_25;
  undefined4 local_24;
  undefined2 local_20;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined4 local_1c;
  undefined2 local_18;
  undefined1 local_16;
  undefined1 local_15;
  undefined4 local_14;
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  local_98 = 0x20;
  local_96 = 0;
  local_95 = 0;
  local_94 = 4;
  local_90 = 0x15;
  local_8e = 1;
  local_8d = 0;
  local_8c = 0xc000003e;
  local_88 = 6;
  local_86 = 0;
  local_85 = 0;
  local_84 = 0;
  ret = 0x20;
  local_7e = 0;
  local_7d = 0;
  local_7c = 0;
  buf = 0x35;
  local_76 = 0;
  local_75 = 1;
  local_74 = 0x40000000;
  local_70 = 0x15;
  local_6e = 0;
  local_6d = 10;
  local_6c = 0xffffffff;
  local_68 = 0x15;
  local_66 = 9;
  local_65 = 0;
  local_64 = 2;
  local_60 = 0x15;
  local_5e = 8;
  local_5d = 0;
  local_5c = 0x39;
  local_58 = 0x15;
  local_56 = 7;
  local_55 = 0;
  local_54 = 0x3a;
  local_50 = 0x15;
  local_4e = 6;
  local_4d = 0;
  local_4c = 0x3b;
  local_48 = 0x15;
  local_46 = 5;
  local_45 = 0;
  local_44 = 0x65;
  local_40 = 0x15;
  local_3e = 4;
  local_3d = 0;
  local_3c = 0x101;
  local_38 = 0x15;
  local_36 = 3;
  local_35 = 0;
  local_34 = 0x142;
  local_30 = 0x15;
  local_2e = 2;
  local_2d = 0;
  local_2c = 0x1ac;
  local_28 = 0x15;
  local_26 = 1;
  local_25 = 0;
  local_24 = 0x1d3;
  local_20 = 6;
  local_1e = 0;
  local_1d = 0;
  local_1c = 0x7fff0000;
  local_18 = 6;
  local_16 = 0;
  local_15 = 0;
  local_14 = 0;
  local_a8[0] = 0x11;
  local_a0 = &local_98;
  prctl(0x26,1,0,0,0);
  prctl(0x16,2,local_a8);
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return;
}

