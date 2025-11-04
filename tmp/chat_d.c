
/* WARNING: Unknown calling convention */

int main(void)

{
  long lVar1;
  user_t user_00;
  int iVar2;
  int iVar3;
  long in_FS_OFFSET;
  int cmd;
  user_t user;
  
  lVar1 = *(long *)(in_FS_OFFSET + 0x28);
  setbuf(stdout,(char *)0x0);
  setbuf(stdin,(char *)0x0);
  setbuf(stderr,(char *)0x0);
  puts("Welcome!\n");
  iVar2 = set_username(&user);
  if (iVar2 == 0) {
LAB_00101280:
    do {
      puts("\nPlease choose cmd!");
      puts("1) Add note.");
      puts("2) Write memo.");
      puts("3) Show memo.");
      puts("4) Show user info");
      printf("> ");
      __isoc99_scanf("%d%*c",&cmd);
      if (cmd == 3) {
        iVar3 = show_memo(&user);
      }
      else if (cmd < 4) {
        if (cmd == 1) {
          iVar3 = add_note(&user);
        }
        else {
          if (cmd != 2) {
LAB_001013ad:
            puts("cmd is invalid.");
            goto LAB_00101280;
          }
          iVar3 = write_memo(&user);
        }
      }
      else if (cmd == 4) {
        iVar3 = show_user(&user);
      }
      else {
        if (cmd != 99) goto LAB_001013ad;
        user_00.name[8] = user.name[8];
        user_00.name[9] = user.name[9];
        user_00.name[10] = user.name[10];
        user_00.name[0xb] = user.name[0xb];
        user_00.name[0xc] = user.name[0xc];
        user_00.name[0xd] = user.name[0xd];
        user_00.name[0xe] = user.name[0xe];
        user_00.name[0xf] = user.name[0xf];
        user_00.name[0] = user.name[0];
        user_00.name[1] = user.name[1];
        user_00.name[2] = user.name[2];
        user_00.name[3] = user.name[3];
        user_00.name[4] = user.name[4];
        user_00.name[5] = user.name[5];
        user_00.name[6] = user.name[6];
        user_00.name[7] = user.name[7];
        user_00.mode[0] = user.mode[0];
        user_00.mode[1] = user.mode[1];
        user_00.mode[2] = user.mode[2];
        user_00.mode[3] = user.mode[3];
        user_00.mode[4] = user.mode[4];
        user_00.mode[5] = user.mode[5];
        user_00.mode[6] = user.mode[6];
        user_00.mode[7] = user.mode[7];
        user_00.mode[8] = user.mode[8];
        user_00.mode[9] = user.mode[9];
        user_00.mode[10] = user.mode[10];
        user_00.mode[0xb] = user.mode[0xb];
        user_00.mode[0xc] = user.mode[0xc];
        user_00.mode[0xd] = user.mode[0xd];
        user_00.mode[0xe] = user.mode[0xe];
        user_00.mode[0xf] = user.mode[0xf];
        user_00.note[0] = user.note[0];
        user_00.note[1] = user.note[1];
        user_00.note[2] = user.note[2];
        user_00.note[3] = user.note[3];
        user_00.note[4] = user.note[4];
        user_00.note[5] = user.note[5];
        user_00.note[6] = user.note[6];
        user_00.note_cnt = user.note_cnt;
        user_00._92_4_ = user._92_4_;
        iVar3 = show_flag(user_00);
      }
    } while (iVar3 == 0);
    puts("error: please retry.");
  }
  else {
    puts("error: failed set username");
  }
  if (lVar1 == *(long *)(in_FS_OFFSET + 0x28)) {
    return iVar2;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}

