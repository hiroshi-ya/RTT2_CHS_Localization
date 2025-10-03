# PSP游戏《异形战机战略版2：苦涩巧克力行动》中文本地化项目自建指南

本文档为本项目的搭建指南。如果您希望直接使用搭建好的补丁，请直接前往[发布页](https://github.com/hiroshi-ya/RTT2_CHS_Localization/releases)获取补丁。如果您希望自行使用本项目的所有素材自行搭建项目，请继续阅读。

## 必备工具

1) 您需要安装`python`（作者使用的是`3.13.5`）以运行所有用于搭建的脚本程序。
   - 您还需要`numpy`模块（作者使用的是`2.3.2`）。
   - 您还需要`pillow`模块（作者使用的是`11.3.0`）。
2) 您需要使用`UMDGen`程序对镜像文件进行解封/封装工作（解封也可以由任意支持`iso`文件格式的压缩软件进行）。
3) 您需要使用`WQSG`程序（作者使用的是`v2012.12070`）对二进制文件执行文字编码导入工作。

备注：如果您不知道上哪里获取`UMDGen`等程序，可以参考[这个仓库](https://github.com/Little-Data/Gametoolkit/releases/tag/V1.0)。

## 搭建步骤

1) `git fork https://github.com/hiroshi-ya/RTT2_CHS_Localization.git`
2) `cd RTT2_CHS_Localization`
3) 使用`UMDGen`打开您的原版镜像文件：
   - 将`UMD/PSP_GAME/SYSDIR/EBOOT.BIN`复制两份，放置于：
     -  `RTT2_CHS_Localization/eboots/`文件夹内 
     -  `RTT2_CHS_Localization/eboots/eboot_backup/`文件夹内
   - 将`UMD/PSP_GAME/USRDIR/`文件夹下的`CMN.DAT`以及`CMN.FAT`放置于`RTT2_CHS_Localization/CMN/`文件夹内。
4) `cd RTT2_CHS_Localization/scripts`
5) 使用`python`执行脚本`top_unpack.py`：
   `python top_unpack.py`
6) 使用`python`执行脚本`sub_unpack.py`：
   `python sub_unpack.py`
   - 运行`sub_unpack.py`时，输入：`sub_list.txt`
7) 使用`python`执行脚本`font_fuse.py`：
   `python font_fuse.py`
8) 使用`python`执行脚本`cfg_merge.py`：
    `python cfg_merge.py`
9)  使用`python`执行脚本`char_check.py`：
    `python char_check.py`
10) 此时，`RTT2_CHS_Localization/CMN/CMN/CFG/MOD/`文件夹下应会出现`CFG.BIN.TXT`文件。
11) 打开`WQSG`，选择`导文本`->`导入文本`模式：
    1) 点击`码表`，选择：`RTT2_CHS_Localization/sources/enc_table/Shift-JIS-work.tbl`
    2) 确保勾选`文本在同目录`
    3) 取消勾选`验证码表重复`、`使用控制码表`、`长度不足中止`
    4) `填充选项`选择`单字节填充`并把下方的`20`更改为`00`
    5) 点击`开始导入`，选择`RTT2_CHS_Localization/CMN/CMN/CFG/MOD/CFG.BIN`
    6) 点击`开始导入`，选择`RTT2_CHS_Localization/eboots/EBOOT.BIN`
12) 使用`python`执行脚本`cfg_split.py`：
    `python cfg_merge.py`
13) 使用`python`执行脚本`sub_repack.py`：
    `python sub_repack.py`
    - 运行`sub_repack.py`时，输入：`all`
14) 使用`python`执行脚本`top_repack.py`：
    `python top_repack.py`
15) 使用`python`执行脚本`mod_applier.py`：
    `python mod_applier.py`
    - 运行`mod_applier.py`时，如果您希望将[数值改动](STATSMOD.md)融合进游戏，请输入`3`
    - 否则请输入`2`
16) 此时，`RTT2_CHS_Localization/eboots/eboot_backup/`文件夹下应会出现`EBOOT.BIN`文件；`RTT2_CHS_Localization/outputs/`文件夹下应会出现`CMN.DAT`以及`CMN.FAT`文件。
17) 回到`UMDGen`：
    - 将`UMD/PSP_GAME/SYSDIR/EBOOT.BIN`替换为
    - 将`UMD/PSP_GAME/USRDIR/CMN/CMN.DAT`替换为`RTT2_CHS_Localization/outputs/CMN.DAT`
    - 将`UMD/PSP_GAME/USRDIR/CMN/CMN.FAT`替换为`RTT2_CHS_Localization/outputs/CMN.FAT`
18) 替换完成后，将当前`UMDGen`里的所有文件另存为（Save）新的镜像文件。
