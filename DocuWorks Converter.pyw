# -*- coding: UTF-8 -*-

'''
---------------------------------------------------------------------------
 FileName : DocuWorks Converter.pyw
 Overview : DosuWorks文書(xdw)をTIFF・PDF・BMP・JPEGに(一括)変換する

 Copyright(c) 2016-2017 Bridge Software All Right Reserved.
---------------------------------------------------------------------------

----------------------------------------------------------------------------
 Revision History
----------------------------------------------------------------------------
 Version 1.0.3
 Date    2017年2月7日
 Content Python3に移行。プログレスダイアログの挙動を変更。その他細かい修正。

 Version 1.0.2
 Date    2016年11月1日
 Content 変換処理をキャンセルできない不具合、ファイル名重複時の処理が機能していない不具合を修正

 Version 1.0.1
 Date    2016年6月8日
 Content 変換前にソートを行うよう修正

 Version 1.0.0
 Date    2016年6月6日
 Content 新規作成
----------------------------------------------------------------------------
'''

import os
import wx
import sys
import glob
import xdwlib
import xml.etree.ElementTree as ET
from wx.lib.buttons import ThemedGenBitmapTextButton as GBT_Button

my = os.path.dirname(os.path.abspath(sys.argv[0]))

# 設定ファイル = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
xml = ET.parse(my + '\\options\\Setting.xml')
input_path = []  # 変換元フォルダパス
for a in range(1, 11):
    R = xml.find('path01-%s' % a).text
    if R is not None:
        input_path.append(R)
output_path = []  # 変換先フォルダパス
for b in range(1, 11):
    M = xml.find('path02-%s' % b).text
    if M is not None:
        output_path.append(M)
pic_type = int(xml.find('format').text)  # フォーマット
dpi = int(xml.find('dpi').text)  # 解像度
comp = int(xml.find('comp').text)  # 圧縮形式
X = int(xml.find('x').text)  # x座標
Y = int(xml.find('y').text)  # y座標


def scale_bitmap(bitmap, width, height):
    """ イメージサイズ変換 """
    image = wx.Bitmap.ConvertToImage(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.Bitmap(image)
    return result


class MyFileDropTarget(wx.FileDropTarget):
    """ ドラッグ＆ドロップクラス(run_button用) """
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        # ドロップされたファイルの中でxdwのものだけを取得
        ext = []
        for f in filenames:
            if ".xdw" in f:
                ext.append(f)

        wx.CallAfter(self.after, filenames, ext)

        return 0

    def after(self, filenames, ext):
        # 引数を作成
        in_dir = os.path.dirname(filenames[0])  # 変換元フォルダパス
        out_dir = self.window.path02.GetValue()  # 出力先フォルダパス
        image_type = self.window.radiobox01.GetSelection()  # 画像種類インデックス 0:TIFF 1:BMP 2:PDF 3:JPEG
        compre = self.window.combo02.GetSelection()  # 圧縮形式
        resolution = int(self.window.combo01.GetValue())  # 解像度
        target_page01 = self.window.radio_button01.GetValue()  # 全ページ
        target_page02 = self.window.radio_button02.GetValue()  # 指定ページ
        color_type = self.window.radiobox02.GetSelection()  # カラー種別
        DW_list = ext
        DW_list.sort()

        # Appクラスのrun関数を実行
        self.window.run(in_dir, out_dir, image_type, compre, resolution, target_page01, target_page02, color_type, DW_list)


class MyFileDropTarget01(wx.FileDropTarget):
    """ ドラッグ＆ドロップクラス(参照ボタン1用) """
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        all_item = self.window.path01.GetItems()

        if os.path.isdir(filenames[0]):
            insert_item = filenames[0]
        else:
            insert_item = os.path.dirname(filenames[0])

        # 既存項目に同じパスが含まれているかチェック
        if insert_item in all_item:
            ind = all_item.index(insert_item)
            all_item.pop(ind)

        all_item.insert(0, insert_item)
        self.window.path01.Clear()
        self.window.path01.AppendItems(all_item)
        self.window.path01.SetSelection(0)

        return 0


class MyFileDropTarget02(wx.FileDropTarget):
    """ ドラッグ＆ドロップクラス(参照ボタン2用) """
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        all_item = self.window.path02.GetItems()

        if os.path.isdir(filenames[0]):
            insert_item = filenames[0]
        else:
            parent = os.path.dirname(filenames[0])
            insert_item = parent

        # 既存項目に同じパスが含まれているかチェック
        if insert_item in all_item:
            ind = all_item.index(insert_item)
            all_item.pop(ind)

        all_item.insert(0, insert_item)
        self.window.path02.Clear()
        self.window.path02.AppendItems(all_item)
        self.window.path02.SetSelection(0)

        return 0


class App(wx.Frame):
    """ メインクラス """
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 600), style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.CreateStatusBar()
        self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, 'メイリオ'))
        self.SetIcon(wx.Icon(my + "\\options\\image\\convert.ico", wx.BITMAP_TYPE_ICO))
        self.SetPosition(wx.Point(X, Y))
        self.Bind(wx.EVT_CLOSE, self.close)

        p = wx.Panel(self, wx.ID_ANY)
        p.Bind(wx.EVT_ENTER_WINDOW, self.leave)

        # 「変換元」関連
        label01 = wx.StaticText(p, wx.ID_ANY, '変換元：')
        if len(input_path) == 0:
            first01 = ""
        else:
            first01 = input_path[0]
        self.path01 = wx.ComboBox(p, wx.ID_ANY, first01, choices=input_path, style=wx.CB_DROPDOWN)
        self.path01.SetToolTip(wx.ToolTip('ここにフォルダをドロップすると変換元フォルダに設定します'))
        self.path01.SetDropTarget(MyFileDropTarget01(self))
        ref_button01 = wx.Button(p, 1, '参照', size=(50, 30))
        ref_button01.Bind(wx.EVT_BUTTON, self.selectdir)
        ref_button01.Bind(wx.EVT_ENTER_WINDOW, self.in_over)
        box01 = wx.BoxSizer(wx.HORIZONTAL)
        box01.Add(label01, flag=wx.TOP, border=5)
        box01.Add(self.path01, flag=wx.LEFT | wx.RIGHT, border=10, proportion=1)
        box01.Add(ref_button01)

        # 「出力先」　関連
        label02 = wx.StaticText(p, wx.ID_ANY, '出力先：')
        if len(output_path) == 0:
            first02 = ""
        else:
            first02 = output_path[0]
        self.path02 = wx.ComboBox(p, wx.ID_ANY, first02, choices=output_path, style=wx.CB_DROPDOWN)
        self.path02.SetToolTip(wx.ToolTip('ここにフォルダをドロップすると出力先フォルダに設定します'))
        self.path02.SetDropTarget(MyFileDropTarget02(self))
        ref_button02 = wx.Button(p, 2, '参照', size=(50, 30))
        ref_button02.Bind(wx.EVT_BUTTON, self.selectdir)
        ref_button02.Bind(wx.EVT_ENTER_WINDOW, self.out_over)
        box02 = wx.BoxSizer(wx.HORIZONTAL)
        box02.Add(label02, flag=wx.TOP, border=5)
        box02.Add(self.path02, flag=wx.LEFT | wx.RIGHT, border=10, proportion=1)
        box02.Add(ref_button02)

        # 初期設定 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if pic_type == 0:  # TIFF
            img = wx.Bitmap(my + '\\options\\image/tiff.ico')
            array04 = ("圧縮なし", "Pacbits", "JPEG", "JPEG(TTN2)", "G4")

        elif pic_type == 1:  # BMP
            img = wx.Bitmap(my + '\\options\\image/bmp.ico')
            array04 = ['']

        elif pic_type == 2:  # PDF
            img = wx.Bitmap(my + '\\options\\image/pdf.ico')
            array04 = ['']

        elif pic_type == 3:  # JPG
            img = wx.Bitmap(my + '\\options\\image/jpg.ico')
            array04 = ('標準', '圧縮率優先', '画質優先')
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # 「フォーマット」関連
        array01 = ("TIFFファイル", "ビットマップファイル", "PDFファイル", "JPEGファイル")
        self.radiobox01 = wx.RadioBox(p, wx.ID_ANY, "画像種類", choices=array01, style=wx.RA_HORIZONTAL, majorDimension=2)
        self.radiobox01.Bind(wx.EVT_RADIOBOX, self.check_change01)
        self.radiobox01.SetSelection(pic_type)
        img = scale_bitmap(img, 100, 100)
        self.bitmap = wx.StaticBitmap(p, wx.ID_ANY, img, size=(100, 100))
        self.bitmap.Bind(wx.EVT_ENTER_WINDOW, self.pic_over)
        box03 = wx.BoxSizer(wx.HORIZONTAL)
        box03.Add(self.radiobox01, proportion=1)
        box03.Add(self.bitmap, flag=wx.LEFT, border=10)

        # 「圧縮形式」関連
        label06 = wx.StaticText(p, wx.ID_ANY, '圧縮形式：')
        self.combo02 = wx.ComboBox(p, wx.ID_ANY, "", choices=array04, size=(150, 30), style=wx.CB_READONLY)
        self.combo02.SetSelection(comp)
        self.combo02.Bind(wx.EVT_ENTER_WINDOW, self.combo02_over)
        box06 = wx.BoxSizer(wx.HORIZONTAL)
        box06.Add(wx.Size(20, 0))
        box06.Add(label06, flag=wx.TOP, border=5)
        box06.Add(self.combo02)

        # 「解像度」関連
        label04 = wx.StaticText(p, wx.ID_ANY, '解像度：')
        array03 =("200", "250", "300", "400", "600")
        self.combo01 = wx.ComboBox(p, wx.ID_ANY, "", choices=array03, size=(80, 30), style=wx.CB_DROPDOWN)
        self.combo01.SetValue(str(dpi))
        self.combo01.Bind(wx.EVT_ENTER_WINDOW, self.combo01_over)
        label05 = wx.StaticText(p, wx.ID_ANY, 'dpi')
        box05 = wx.BoxSizer(wx.HORIZONTAL)
        box05.Add(wx.Size(20, 0))
        box05.Add(label04, flag=wx.TOP, border=5)
        box05.Add(self.combo01)
        box05.Add(label05, flag=wx.TOP | wx.LEFT, border=5)

        # 「圧縮形式」ボックス+「解像度」ボックス
        minibox02 = wx.BoxSizer(wx.HORIZONTAL)
        minibox02.Add(box06)
        minibox02.Add(wx.Size(30, 0))
        minibox02.Add(box05)

        # 「ページ」関連
        self.radio_button01 = wx.RadioButton(p, 1, '全ページ')
        self.radio_button01.Bind(wx.EVT_RADIOBUTTON, self.check_change02)
        self.radio_button01.SetValue(True)
        self.radio_button02 = wx.RadioButton(p, 2, 'ページ指定')
        self.radio_button02.Bind(wx.EVT_RADIOBUTTON, self.check_change02)
        self.start_page = wx.TextCtrl(p, wx.ID_ANY, size=(70, 25))
        label03 = wx.StaticText(p, wx.ID_ANY, '～')
        self.end_page = wx.TextCtrl(p, wx.ID_ANY, size=(70, 25))
        self.start_page.Disable()
        self.end_page.Disable()

        # ページ入力関連のまとめボックス
        minibox01 = wx.BoxSizer(wx.HORIZONTAL)
        minibox01.Add(self.start_page)
        minibox01.Add(label03, flag=wx.TOP, border=5)
        minibox01.Add(self.end_page)

        # ラジオボタン2とページ入力関連まとめの結合ボックス
        middlebox = wx.BoxSizer(wx.HORIZONTAL)
        middlebox.Add(self.radio_button02)
        middlebox.Add(minibox01)

        s_box = wx.StaticBox(p, wx.ID_ANY, '対象ページ')

        # ラジオボタン1とラジオボタン2関連まとめのボックス
        box04 = wx.StaticBoxSizer(s_box, wx.HORIZONTAL)
        box04.Add(self.radio_button01, flag=wx.ALL, border=10, proportion=1)
        box04.Add(middlebox, flag=wx.ALL, border=10, proportion=1)
        box04.Add(wx.Size(30, 0))

        # 「カラー」関連
        array02 = ("白黒", "カラー", "カラーを白黒")
        self.radiobox02 = wx.RadioBox(p, wx.ID_ANY, "カラー", choices=array02, style=wx.RA_HORIZONTAL)
        self.radiobox02.Bind(wx.EVT_RADIOBOX, self.check_change03)

        # 変換開始ボタン
        self.run_button = GBT_Button(p, wx.ID_ANY, scale_bitmap(wx.Bitmap(my + '\\options\\image\\convert.ico'), 50, 50), '　Start Convert!!')
        self.run_button.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'メイリオ'))
        self.run_button.Bind(wx.EVT_BUTTON, self.decison)
        self.run_button.Bind(wx.EVT_ENTER_WINDOW, self.r_over)
        self.run_button.SetDropTarget(MyFileDropTarget(self))

        # メインレイアウト
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(box01, flag=wx.EXPAND | wx.ALL, border=10)  # 「変換元」関連
        layout.Add(box02, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)  # 「変換先」関連
        layout.Add(wx.StaticLine(p), flag=wx.GROW | wx.TOP | wx.BOTTOM, border=10)
        layout.Add(box03, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)  # 「フォーマット」関連
        layout.Add(wx.Size(0, 10))
        layout.Add(minibox02, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)  # 「圧縮形式」関連+「解像度」関連
        layout.Add(wx.Size(0, 10))
        layout.Add(box04, flag=wx.EXPAND | wx.ALL, border=10)  # 「ページ」関連
        layout.Add(self.radiobox02, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)  # 「カラー」関連
        layout.Add(self.run_button, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10, proportion=1)
        p.SetSizer(layout)

        self.run_button.SetFocus()

        self.combo_check()

        self.Show()

        # パスの初期設定 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
        # 各パスの数が空の場合に実行
        if len(input_path) == 0 or len(output_path) == 0:
            dialog = wx.MessageDialog(None, '初期設定を開始します。', '初期設定', wx.OK)
            dialog.ShowModal()
            dialog.Destroy()

            # 変換元が空白の場合
            if len(input_path) == 0 :
                # 変換元フォルダの選択
                in_dialog = wx.DirDialog(None, '変換元フォルダ(DW文書が保存されているフォルダ)を選択してください。')
                result1 = in_dialog.ShowModal()

                if result1 == wx.ID_OK:
                    new_in_folder = in_dialog.GetPath()
                    input_path.append(new_in_folder)
                    self.path01.Append(new_in_folder)
                    self.path01.SetSelection(0)

            if len(output_path) == 0:
                # 出力先フォルダの選択
                out_dialog = wx.DirDialog(None, '出力先フォルダ(変換した文書の保存先フォルダ)を選択してください。')
                result2 = out_dialog.ShowModal()

                if result2 == wx.ID_OK:
                    new_out_folder = out_dialog.GetPath()
                    output_path.append(new_out_folder)
                    self.path02.Append(new_out_folder)
                    self.path02.SetSelection(0)

            # 両方ともパスが設定されたかチェック
            i_path = len(self.path01.GetItems())
            o_path = len(self.path02.GetItems())

            # どちらも1以上であればOK
            if i_path >= 1 and o_path >= 1:
                # 設定完了
                end_dialog = wx.MessageDialog(None, '初期設定が正常に終了しました。', '設定完了', wx.OK)
                end_dialog.ShowModal()
                end_dialog.Destroy()

            # どちらかが0であれば異常=> アプリ強制終了
            else:
                end_dialog = wx.MessageDialog(None, '初期設定が正常に終了しませんでした。\n\n再度アプリを起動し、初期設定を行ってください。', '設定エラー', wx.OK)
                end_dialog.ShowModal()
                end_dialog.Destroy()
                self.Close(True)

    def combo_check(self):
        """ 圧縮形式コンボボック部の有効無効チェック """
        if self.radiobox01.GetSelection() == 1:
            self.combo02.Disable()
        elif self.radiobox01.GetSelection() == 2:
            if self.radiobox02.GetSelection() in [0, 2]:
                self.combo02.Disable()

    # マウスオーバーイベント = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def in_over(self, event):
        self.SetStatusText('変換元フォルダを変更します')

    def out_over(self, event):
        self.SetStatusText('出力先フォルダを変更します')

    def pic_over(self, event):
        self.SetStatusText('選択中の画像種類は%sです' % self.radiobox01.GetStringSelection())

    def combo01_over(self, event):
        self.SetStatusText('解像度を変更します')

    def combo02_over(self, event):
        self.SetStatusText('圧縮形式を変更します')

    def r_over(self, event):
        self.SetStatusText('このボタンをクリックするか、xdwファイルをボタン上にドロップしてください')

    def leave(self, event):
        self.SetStatusText('')

    # フォルダ参照 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def selectdir(self, event):
        ID = event.GetId()

        # その時点のテキストボックスの幅を取得しておく
        haba = self.path01.GetSize()

        # 初期表示フォルダパスの決定
        if ID == 1:
            folder = self.path01.GetValue()
        else:
            folder = self.path02.GetValue()

        # ダイアログの表示
        dialog = wx.DirDialog(None, 'フォルダの選択', defaultPath=folder)
        result = dialog.ShowModal()
        dialog.Destroy()

        # ダイアログの結果がOKの場合
        if result == wx.ID_OK:
            getpath = dialog.GetPath()

            # 既存項目の取得
            if ID == 1:
                all_item = self.path01.GetItems()
            elif ID == 2:
                all_item = self.path02.GetItems()

            # 既存項目に同じパスが含まれているかチェック
            if getpath in all_item:
                ind = all_item.index(getpath)
                all_item.pop(ind)

            # インデックス0にドロップしたアイテムを挿入
            all_item.insert(0, getpath)

            if ID == 1:
                self.path01.Clear()
                self.path01.AppendItems(all_item)
                self.path01.SetSelection(0)
                self.path01.SetSize(haba)

            elif ID == 2:
                self.path02.Clear()
                self.path02.AppendItems(all_item)
                self.path02.SetSelection(0)
                self.path02.SetSize(haba)

    # 「画像種類」選択変更イベント = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def check_change01(self, event):
        # 選択項目インデックスを取得
        select = self.radiobox01.GetSelection()
        if select == 0:  # TIFF
            self.combo02.Enable()
            img = wx.Bitmap(my + '\\options\\image\\tiff.ico')
            press = ("圧縮なし", "Packbits", "JPEG", "JPEG(TTN2)", "G4")
            index = 4
        elif select == 1:  # BMP
            self.combo02.Disable()
            img = wx.Bitmap(my + '\\options\\image\\bmp.ico')
            press = ['']
            index = 0
        elif select == 2:  # PDF
            img = wx.Bitmap(my + '\\options\\image\\pdf.ico')
            # カラーの場合のみ
            color = self.radiobox02.GetSelection()
            if color == 1:
                self.combo02.Enable()
                press = ('標準', '標準(高圧縮)', '圧縮率優先', '圧縮率優先(高圧縮)', '画質優先', '画質優先(高圧縮)')
            else:
                self.combo02.Disable()
                press = ['']
            index = 0
        elif select == 3:  # jpg
            self.combo02.Enable()
            img = wx.Bitmap(my + '\\options\\image\\jpg.ico')
            press = ('標準', '圧縮率優先', '画質優先')
            index = 0

        # 画像の変更
        img = scale_bitmap(img, 100, 100)
        self.bitmap.SetBitmap(img)

        # 圧縮形式内選択肢の変更
        self.combo02.SetItems(press)
        self.combo02.SetSelection(index)

    # 「対象ページ」チェック変更イベント = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def check_change02(self, event):
        # IDを取得
        ID = event.GetId()

        if ID == 2:  # ページ指定の場合
            self.start_page.Enable()
            self.end_page.Enable()

        elif ID == 1:  # 全ページの場合
            self.start_page.SetValue("")
            self.end_page.SetValue("")
            self.start_page.Disable()
            self.end_page.Disable()

    # 「カラー」チェック変更イベント = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def check_change03(self, event):
        select = self.radiobox02.GetSelection()

        # カラーを選択した場合
        if select == 1:
            if self.radiobox01.GetSelection() == 2:
                self.combo02.Enable()
                press = ('標準', '標準(高圧縮)', '圧縮率優先', '圧縮率優先(高圧縮)', '画質優先', '画質優先(高圧縮)')

                # 圧縮形式内選択肢の変更
                self.combo02.SetItems(press)
                self.combo02.SetSelection(0)
        else:
            if self.radiobox01.GetSelection() == 2:
                self.combo02.Disable()
                press = ['']

                # 圧縮形式内選択肢の変更
                self.combo02.SetItems(press)
                self.combo02.SetSelection(0)

    # ターゲット確定 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def decison(self, event):

        # 各値を取得
        in_dir = self.path01.GetValue()  # 変換元フォルダパス
        out_dir = self.path02.GetValue()  # 出力先フォルダパス
        image_type = self.radiobox01.GetSelection()  # 画像種類インデックス 0:TIFF 1:BMP 2:PDF 3:JPEG
        compre = self.combo02.GetSelection()  # 圧縮形式
        resolution = int(self.combo01.GetValue())  # 解像度
        target_page01 = self.radio_button01.GetValue()  # 全ページ
        target_page02 = self.radio_button02.GetValue()  # 指定ページ
        color_type = self.radiobox02.GetSelection()  # カラー種別

        # 変換元フォルダ内のxdwファイルをリスト化
        DW_list = glob.glob(in_dir + "\\*.xdw")
        DW_list.sort()

        # 変換処理関数の呼び出し
        self.run(in_dir, out_dir, image_type, compre, resolution, target_page01, target_page02, color_type, DW_list)

    # 変換処理 = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    def run(self, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9):
        out_dir = arg2
        image_type = arg3
        compre = arg4
        resolution = arg5
        target_page01 = arg6
        color_type = arg8
        DW_list = arg9

        # 拡張子・フォーマット・圧縮形式の設定 0:TIFF 1:BMP 2:PDF 3:JPEG
        if image_type == 0:  # TIFF
            ext = ".tif"
            i = 'TIFF'

            # 圧縮形式 ("圧縮なし", "Packbits", "JPEG", "JPEG(TTN2)", "G4")
            if compre == 0:
                com = 'NOCOMPRESS'
            elif compre == 1:
                com = 'PACKBITS'
            elif compre == 2:
                com = 'JPEG'
            elif compre == 3:
                com = 'JPEG_TTN2'
            elif compre == 4:
                com = 'G4'

        elif image_type == 1:  # BMP
            ext = ".bmp"
            i = 'BMP'
            com = 0

        elif image_type == 2:  # PDF
            ext = ".pdf"
            i = 'PDF'
            # カラーの場合
            if color_type == 1:
                # 圧縮形式 ('標準', '標準(高圧縮)', '圧縮率優先', '圧縮率優先(高圧縮)', '画質優先', '画質優先(高圧縮)')
                if compre == 0:
                    com = 'NORMAL'
                elif compre == 1:
                    com = 'MRC_NORMAL'
                elif compre == 2:
                    com = 'HIGHCOMPRESS'
                elif compre == 3:
                    com = 'MRC_HIGHCOMPRESS'
                elif compre == 4:
                    com = 'HIGHQUALITY'
                elif compre == 5:
                    com = 'MRC_HIGHQUALITY'

            # カラー以外の場合
            else:
                com = 0

        elif image_type == 3:  # JPEG
            ext = ".jpg"
            i = 'JPEG'
            # 圧縮形式　('標準', '圧縮率優先', '画質優先')
            if compre == 0:
                com = 'NORMAL'
            elif compre == 1:
                com = 'HIGHCOMPRESS'
            elif compre == 2:
                com = 'HIGHQUALITY'

        # xdwファイルが無い場合はメッセージ
        if len(DW_list) == 0:
            error_dialog = wx.MessageDialog(None, '指定フォルダ内にDW文書が存在しません', 'エラー', wx.ICON_ERROR)
            error_dialog.ShowModal()

        # xdwファイルがある場合は続行
        else:
            # プログレスダイアログの作成
            p_dialog = wx.ProgressDialog('DocuWorks Converterは一所懸命変換しています', '0 / %s ファイル\n　ファイル名 ：\n　ページ数　 ：\n　サイズ　　 ：' % len(DW_list), maximum=len(DW_list), style=wx.PD_CAN_ABORT | wx.PD_SMOOTH | wx.PD_AUTO_HIDE)

            # 変換開始
            m = 0
            no_push = 0
            for r in DW_list:
                # ファイル名の取得
                basicname = os.path.basename(r)
                name = basicname.split(".")[0]
                kb = int(os.path.getsize(r) / 1024)
                mb = round(os.path.getsize(r) / 1024 ** 2, 1)

                # DW文書を開く
                doc = xdwlib.xdwopen(r)

                # ページの確認＆変数作成
                if target_page01:  # 全ページの時
                    page = (0, doc.pages)

                else:
                    # ページ指定の時
                    # ページ数が1枚の場合
                    if doc.pages == 1:
                        page = (0, doc.pages)

                    else:
                        # 開始ページと終了ページ
                        first_page = int(self.start_page.GetValue())
                        finish_page = int(self.end_page.GetValue())

                        # 開始ページのチェック
                        if first_page > doc.pages:
                            before = doc.pages
                        elif first_page == doc.pages:
                            before = 0
                        else:
                            before = first_page - 1

                        # 終了ページのチェック
                        if finish_page >= doc.pages:
                            after = doc.pages
                        else:
                            after = finish_page

                        # ページ確定
                        page = (before, after)

                # 同名ファイルの存在確認
                new_file_path = out_dir + "\\" + name + ext
                new = name + ext

                # 存在の確認
                if os.path.isfile(new_file_path):

                    is_dialog = wx.MessageDialog(None, '出力先フォルダに %s がすでに存在しています。\n上書きしてもよろしいですか？\n(「いいえ」の場合は別名で保存します)' % new, 'info', wx.YES_NO)
                    is_result = is_dialog.ShowModal()

                    if is_result == wx.ID_YES:
                        # 既存ファイルを削除
                        os.remove(new_file_path)
                        new_name = new_file_path
                    else:
                        new_name = out_dir + "\\" + name + "_(1)" + ext

                # 存在しない場合
                else:
                    new_name = new_file_path

                # 色コードの作成
                if color_type == 0:
                    c_type = 'MONO'
                elif color_type == 1:
                    c_type = 'COLOR'
                elif color_type == 2:
                    c_type = 'MONO_HIGHQUALITY'

                # 圧縮形式に初期状態を採用
                com2 = com

                # ファイル名の末尾に「C」が付く場合はカラー
                if name[-1:] == "C" or name[-1:] == "c" or name[-1:] == 'ｃ' or name[-1:] == 'Ｃ':
                    c_type = 'COLOR'

                    # さらに、TIFFの場合は圧縮形式をJPEGに変更
                    if image_type == 0:
                       com2 = 'JPEG'

                # 「C」が付かない場合はそのままの圧縮形式を採用
                else:
                    com2 = com

                # プログレスダイアログのアップデート
                m += 1
                action = p_dialog.Update(m - 1, str(m) + ' / %s ファイル\n　ファイル名 ： %s\n　ページ数　 ： %s ページ\n　　サイズ　 ： %s KB (約 %s MB)' % (len(DW_list), basicname, doc.pages, kb, mb))

                if no_push == 0:
                    # キャンセル初回押下時
                    if not action[0]:
                        caution = wx.MessageDialog(None, '処理を中止しますか？', '中止確認', wx.YES_NO)
                        ans = caution.ShowModal()
                        caution.Destroy()

                        if ans == wx.ID_YES:
                            doc.close()
                            break
                        else:
                            no_push += 1
                            p_dialog.Resume()
                    else:
                        p_dialog.Resume()

                # 変換の実行
                doc.export_image(page, new_name, 1, dpi=resolution, color=c_type, format=i, compress=com2, direct=False)
                doc.close()
                p_dialog.Update(m)

            # 完了メッセージ
            finish_dialog = wx.MessageDialog(None, '変換が完了しました。', '完了', wx.OK)
            finish_dialog.ShowModal()
            p_dialog.Destroy()
            finish_dialog.Destroy()
            self.Refresh()

    def close(self, event):
        """ 閉じるイベント """
        self.Destroy()

        # 閉じた時点の各情報を取得
        position = self.GetPosition()  # 表示位置
        input_text = self.path01.GetItems()  # 変換元フォルダパス
        output_text = self.path02.GetItems()  # 出力先フォルダパス
        format_text = self.radiobox01.GetSelection()  # フォーマットのインデックス番号
        dpi_text = self.combo01.GetValue()  # dip値
        comp_text = self.combo02.GetSelection()  # 圧縮形式値

        # 各パスの数を数える
        i_range = self.path01.GetCount()
        o_range = self.path02.GetCount()

        # パス関係を先に処理
        for c in range(1, i_range + 1):
            new_path01 = xml.find('path01-%s' % c)
            new_path01.text = input_text[c - 1]
            if c == 10:
                break

        for d in range(1, o_range + 1):
            new_path02 = xml.find('path02-%s' % d)
            new_path02.text = output_text[d - 1]
            if d == 10:
                break

        # 書き換え先を設定
        new_format = xml.find('format')
        new_dpi = xml.find('dpi')
        new_comp = xml.find('comp')
        new_x = xml.find('x')
        new_y = xml.find('y')

        # xmlファイルを書き換え
        new_format.text = str(format_text)
        new_dpi.text = str(dpi_text)
        new_comp.text = str(comp_text)
        new_x.text = str(position[0])
        new_y.text = str(position[1])

        # XMLファイルの上書き保存
        xml.write(my + '\\options\\Setting.xml', 'utf-8', True)


if __name__ == "__main__":
    app = wx.App()
    App(None, wx.ID_ANY, 'DocuWorks Converter')
    app.MainLoop()