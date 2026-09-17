# by shadowrider
# original: https://github.com/fs-plugins/timFS
#
from . import _
from Components.ActionMap import ActionMap, HelpableActionMap, NumberActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor

from Components.Sources.List import List
from Components.ConfigList import ConfigListScreen
from Components.config import KEY_LEFT, KEY_RIGHT, config, ConfigSubsection, ConfigText, getConfigListEntry, ConfigSelection, ConfigYesNo, NoSave, ConfigInteger

from Screens.HelpMenu import HelpableScreen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Screens.InfoBar import InfoBar
from Screens.InfoBarGenerics import InfoBarChannelSelection
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, loadPNG, eTimer
from Tools.Directories import fileExists
import os

conf_path = "/etc/enigma2/timFSconf"
found_new = False
version = 3.1

try:
	basestring
except NameError:
	basestring = str


# config settings
config.plugins.timFS = ConfigSubsection()
config.plugins.timFS.hits = ConfigSelection(default="0", choices=[("0", _("abc")), ("1", _("hits")), ("2", _("own")), ("3", _("abc,numbers")), ("4", _("hits,numbers")), ("5", _("own,numbers"))])
config.plugins.timFS.fontsize = ConfigSelection(default="24", choices=[("22", "22"), ("24", "24"), ("26", "26"), ("28", "28")])
config.plugins.timFS.hauptmenu = ConfigYesNo(default=False)
config.plugins.timFS.close1 = ConfigYesNo(default=True)
config.plugins.timFS.display = ConfigText(default="1,3,250,4,name,0,14,12")


class tim_list(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 14))
		self.l.setFont(1, gFont("Regular", 16))
		self.l.setFont(2, gFont("Regular", 18))
		self.l.setFont(3, gFont("Regular", 17))
		self.l.setFont(4, gFont("Regular", 22))
		self.l.setFont(5, gFont("Regular", 24))
		self.l.setFont(6, gFont("Regular", 26))
		self.l.setFont(7, gFont("Regular", 20))
		self.l.setFont(8, gFont("Regular", 19))


class timFS_config(Screen, ConfigListScreen, HelpableScreen):

	def __init__(self, session, plugin_path):
		with open("/usr/lib/enigma2/python/Plugins/Extensions/timFS/skin/timFS_config.xml") as tmpskin:
			self.skin = tmpskin.read()
		Screen.__init__(self, session)
		self.plugin_path = plugin_path
		self.skin_path = plugin_path
		self.skinName = "timFS_config"
		self.session = session
		self.setTitle(_("timFS Setup v") + str(version))
		HelpableScreen.__init__(self)
		self.list = []
		self["titel"] = Label("timFS - " + _("The individual menu:") + " " * 10 + _("Settings"))
		self["config2"] = tim_list([])
		self["config3"] = tim_list([])
		self["descrip2"] = Label(_("Settings"))
		self["balken"] = Label()
		self["label_green"] = Label(_("Display"))
		self["label_red"] = Label()
		self["label_yellow"] = Label()
		self["label_blue"] = Label()
		self["pic_red"] = Pixmap()
		self["pic_green"] = Pixmap()
		self["pic_yellow"] = Pixmap()
		self["pic_blue"] = Pixmap()
		self["ok"] = Pixmap()
		self.grau = 0xBEBEBE
		self.grau2 = 0x545454  # BEBEBE
		self.schwarz = 0x000000
		self.color1 = self.grau
		self.color2 = 0xFFFFFF  # schwarz
		self.selected = False
		self.move_on = False
		self.select_screen = 1
		ConfigListScreen.__init__(self, self.list)
		self.list.append(getConfigListEntry(" " * 3 + _("List sort by, with or without a number:"), config.plugins.timFS.hits))
		self.list.append(getConfigListEntry(" " * 3 + _("Show in main menu (reboot required!):"), config.plugins.timFS.hauptmenu))
		self.list.append(getConfigListEntry(" " * 3 + _("Text Size:"), config.plugins.timFS.fontsize))
		self.list.append(getConfigListEntry(" " * 3 + _("Automatically close:"), config.plugins.timFS.close1))

		self["config"].setList(self.list)

		self["timfsKeyActions"] = HelpableActionMap(self, "timfsKeyActions",
			{
			"cancel": (self.saveConfig, _("Save and close")),
			"ok": (self.change_hide, _("Change/Hide Plugin")),
			"red": (self.del_group, _("Delete group")),
			"blue": (self.change_descrip, _("Change Description")),
			"yellow": (self.change_group, _("Change group")),
			"green": (self.add_group, _("Add group")),
			"nextBouquet": (self.cup, _("Next group")),
			"prevBouquet": (self.cdown, _("Previous group")),
			"nextBouquetl": (self.cup, _("Next group")),
			"prevBouquetl": (self.cdown, _("Previous group")),
			"up": (self.up, _("Up")),
			"down": (self.down, _("Down")),
			"right": (self.right, _("Right")),
			"left": (self.left, _("Left")),
			}, -1)

		self.readconfig()
		self.onLayoutFinish.append(self.startup)

	def startup(self):
		self["config2"].instance.setSelectionEnable(0)
		self["config3"].instance.setSelectionEnable(0)

	def right(self):
		if self.select_screen == 1:
			self["config"].handleKey(KEY_RIGHT)
			self.readconfig()
		elif self.select_screen == 2:
			self["config2"].pageDown()
		elif self.select_screen == 3:
			self["config3"].pageDown()
			self.textset()

	def left(self):
		if self.select_screen == 1:
			self["config"].handleKey(KEY_LEFT)
			self.readconfig()
		elif self.select_screen == 2:
			self["config2"].pageUp()
		elif self.select_screen == 3:
			self["config3"].pageUp()
		self.textset()

	def cup(self):
		self["descrip2"].setText("")
		if self.select_screen == 1:
			self.select_screen = 3
			self.screen3a()
		elif self.select_screen == 2:
			self.select_screen = 1
			self.screen1a()
		elif self.select_screen == 3:
			self.select_screen = 2
			self.screen2a()

	def cdown(self):
		self["descrip2"].setText("")
		if self.select_screen == 1:
			self.select_screen = 2
			self.screen2a()
		elif self.select_screen == 2:
			self.select_screen = 3
			self.screen3a()
		elif self.select_screen == 3:
			self.select_screen = 1
			self.screen1a()

	def screen1a(self):
		self["ok"].show()
		self["label_green"].setText(_("Display"))
		self["label_yellow"].setText("")
		self["label_blue"].setText("")
		self["label_red"].setText("")
		self["descrip2"].setText(_("Settings"))
		self["config3"].instance.setSelectionEnable(0)
		self["config2"].instance.setSelectionEnable(0)
		self["config"].instance.setSelectionEnable(1)

	def screen2a(self):  #pluginlist
		self["label_green"].setText(_("Sort"))
		self["label_yellow"].setText(_("Group"))
		self["label_red"].setText("")
		self["label_blue"].setText(_("Rename"))
		self["ok"].show()

		self["config"].instance.setSelectionEnable(0)
		self["config3"].instance.setSelectionEnable(0)
		self["config2"].instance.setSelectionEnable(1)
		self.textset()

	def screen3a(self):  #groups
		self["label_green"].setText(_("Add"))
		self["label_yellow"].setText("")
		self["label_red"].setText(_("Delete"))
		self["label_blue"].setText("")
		self["ok"].hide()
		self["descrip2"].setText(_("Groups"))
		self["label_blue"].setText("")
		self["config2"].instance.setSelectionEnable(0)
		self["config"].instance.setSelectionEnable(0)
		self["config3"].instance.setSelectionEnable(1)

	def textset(self):  #groups
		if len(self["config2"].getCurrent()[0][6]):
			self["descrip2"].setText(_("Description") + ": " + self["config2"].getCurrent()[0][6])
		else:
			self["descrip2"].setText(_("Description") + ": " + self["config2"].getCurrent()[0][1])

	def up(self):
		if self.select_screen == 1:
			if self["config"].getCurrentIndex() <= len(self["config"].list) - 1:
				idx = int(self["config"].getCurrentIndex()) - 1
				self["config"].setCurrentIndex(idx)
		elif self.select_screen == 2:
			self["config2"].up()
			self.textset()
		elif self.select_screen == 3:
			self["config3"].up()

	def down(self):
		if self.select_screen == 1:
			if len(self["config"].list) - 1 > self["config"].getCurrentIndex() and not len(self["config"].list) - 1 == self["config"].getCurrentIndex():
				idx = idx = int(self["config"].getCurrentIndex()) + 1
				self["config"].setCurrentIndex(idx)
		elif self.select_screen == 2:
			self["config2"].down()
			self.textset()
		elif self.select_screen == 3:
			self["config3"].down()

	def readconfig(self):
		listen = read_config()
		self.config_list_select = []
		self.config_list = []
		self.group_list_select = []
		self.group_list = []
		for x in listen[0]:
			self.config_list_select.append(["", x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]])  #(name, hits, hide, sort, group, bez,art,imp,run)
		for x in listen[1]:
			self.config_list_select.append(["", x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9]])  # (None,name, hits, hide, sort, group, bez,art,imp,run)
		if config.plugins.timFS.hits.value == "1" or config.plugins.timFS.hits.value == "4":
			self.config_list_select.sort(key=lambda x: -int(x[2]))
		elif config.plugins.timFS.hits.value == "2" or config.plugins.timFS.hits.value == "5":
			self.config_list_select.sort(key=lambda x: (x[5], int(x[4])))
		else:
			self.config_list_select.sort(key=lambda p: p[1].lower())
		for each in self.config_list_select:
			(nix, name, hits, hide, sort, group, descrip, art, imp, run) = each
			self.config_list.append(self.show_menu(nix, name, hits, hide, sort, group, descrip, art, imp, run))
		self["config2"].l.setList(self.config_list)
		self["config2"].l.setItemHeight(22)

		for x2 in listen[2]:
			self.group_list_select.append(x2)
		for group in self.group_list_select:
			self.group_list.append(self.show_menu_group(group))
		self["config3"].l.setList(self.group_list)
		self["config3"].l.setItemHeight(22)

	def show_menu(self, nix, name, hits, hide, sort, group, descrip, art, imp, run):
		res = [(nix, name, hits, hide, sort, group, descrip, art, imp, run)]
		if int(hide) == 0:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 2), size=(20, 20), png=loadPNG(self.plugin_path + "/skin/on.png"), backcolor=self.schwarz, backcolor_sel=self.grau2))
		else:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 2), size=(20, 20), png=loadPNG(self.plugin_path + "/skin/off.png")))
		res.append(MultiContentEntryText(pos=(50, 0), size=(350, 22), font=8, text=name, flags=RT_HALIGN_LEFT, backcolor=self.schwarz, backcolor_sel=self.grau2))
		res.append(MultiContentEntryText(pos=(360, 0), size=(150, 22), font=8, text=group, flags=RT_HALIGN_LEFT, backcolor=self.schwarz, backcolor_sel=self.grau2))
		res.append(MultiContentEntryText(pos=(535, 0), size=(60, 22), font=8, text=hits, flags=RT_HALIGN_LEFT, backcolor=self.schwarz, backcolor_sel=self.grau2))

		if self.selected and name == self.last_plugin[1]:
			res.append(MultiContentEntryPixmapAlphaTest(pos=(30, 2), size=(20, 20), png=loadPNG(self.plugin_path + "/skin/move.png")))
		return res

	def readgroups(self):
		self.readconfig()

	def show_menu_group(self, group_name):
		res = [(group_name)]
		res.append(MultiContentEntryText(pos=(0, 0), size=(170, 22), font=7, text=group_name, flags=RT_HALIGN_LEFT, color=self.color1, color_sel=self.color1, backcolor=0x2E2E2E, backcolor_sel=self.grau2))
		return res

	def change_group(self):
		if self.select_screen == 2:
			item = self["config2"].getCurrent()[0]
			if item:
				list_name = item[1]  # noqa F841
				group_name = item[5]
				next_name = self.next_item(group_name, self.group_list_select)
				ind = self.config_list_select.index(list(item))
				self.config_list_select[ind][5] = next_name
				write_config(self.config_list_select, [], self.group_list_select)
				self.readconfig()

	def next_item(sel, item, list):
		count = len(list)
		idx = 0
		for each in list:
			if each == item:
				idx += 1
				break
			else:
				idx += 1
		if count == idx:
			return list[0]
		else:
			return list[int(idx)]

	def change_hide(self):
		if self.selected:
			self.select()
		elif self.select_screen == 2:
			item = self["config2"].getCurrent()[0]
			if item:
				try:
					ind = self.config_list_select.index(list(item))
					if self.config_list_select[ind][3] == "1":
						self.config_list_select[ind][3] = "0"
					else:
						self.config_list_select[ind][3] = "1"
					write_config(self.config_list_select, [], self.group_list_select)
					self.readconfig()
				except Exception:
					pass

	def del_group(self):
		if self.select_screen == 3:
			item = self["config3"].getCurrent()
			if item:
				list_name = item[0]
				if list_name != _("main group") and list_name in self.group_list_select:
					self.group_list_select.remove(list_name)
					write_config(self.config_list_select, [], self.group_list_select)
					for x in self.config_list_select:
						if x[5] == list_name:
							ind = self.config_list_select.index(x)
							self.config_list_select[ind][5] = _("main group")
							write_config(self.config_list_select, [], self.group_list_select)
					self.readconfig()

	def add_group(self):
		if self.select_screen == 2:
			self.select()
		elif self.select_screen == 3:
			self.session.openWithCallback(self.write_group, VirtualKeyBoard, title=_("Enter group name:"))
		elif self.select_screen == 1:
			self.session.open(setDisplay)

	def write_group(self, group_name=None):
		if group_name and group_name not in self.group_list_select:
			self.group_list_select.append(group_name)
			write_config(self.config_list_select, [], self.group_list_select)
			self.readconfig()

	def change_descrip(self):
		if self.select_screen == 2:
			item = self["config2"].getCurrent()[0][6]
			self.session.openWithCallback(self.write_descrip, VirtualKeyBoard, title=_("Enter Plugin description:"), text=item)

	def write_descrip(self, descrip1=None):
		if descrip1 is not None:
			item = self["config2"].getCurrent()[0]
			if item:
				try:
					ind = self.config_list_select.index(list(item))
					self.config_list_select[ind][6] = descrip1
					write_config(self.config_list_select, [], self.group_list_select)
					self.readconfig()
				except Exception:
					pass

	def select(self):
		if self.select_screen == 2:
			if not self.selected:
				self.last_plugin = self["config2"].getCurrent()[0]
				self.old_idx = self.config_list.index(self["config2"].getCurrent())
				self.last_eintrag = self.config_list[self.old_idx]
				self.selected = True
			else:
				now_idx = self.config_list.index(self["config2"].getCurrent())
				count_move = 0
				del self.config_list[self.old_idx]
				self.config_list.insert(now_idx, self.last_eintrag)
				self.config_list_select = []
				for x in self.config_list:
					s1 = x[0]
					self.config_list_select.append(["", s1[1], s1[2], s1[3], str(count_move), s1[5], s1[6], s1[7], s1[8], s1[9]])
					count_move += 1
				self.selected = False
				write_config(self.config_list_select, [], self.group_list_select)
			self.readconfig()

	def saveConfig(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def exit(self):
		self.close()


class setDisplay(Screen, ConfigListScreen):
	def __init__(self, session):
		with open("/usr/lib/enigma2/python/Plugins/Extensions/timFS/skin/timFS_display.xml") as tmpskin:
			self.skin = tmpskin.read()
		sets = config.plugins.timFS.display.value.split(",")
		if len(sets) < 9:
			sets.extend(("", 0, 0, 0))
		self.zeilen = NoSave(ConfigInteger(int(sets[0]), (1, 2)))
		self.scroll_speed = NoSave(ConfigInteger(int(sets[1]), (0, 99)))
		self.len = NoSave(ConfigInteger(int(sets[2]), (0, 999)))
		self.hp = NoSave(ConfigInteger(int(sets[3]), (0, 99)))
		self.l1t = NoSave(ConfigSelection(default=sets[4], choices=[("name", _("name")), ("group", _("group")), ("", "")]))
		self.l1p = NoSave(ConfigInteger(int(sets[5]), (0, 99)))
		self.l1h = NoSave(ConfigInteger(int(sets[6]), (0, 99)))
		self.l1f = NoSave(ConfigInteger(int(sets[7]), (0, 99)))
		self.l2t = NoSave(ConfigSelection(default=sets[8], choices=[("name", _("name")), ("group", _("group")), ("", "")]))
		self.l2p = NoSave(ConfigInteger(int(sets[9]), (0, 99)))
		self.l2h = NoSave(ConfigInteger(int(sets[10]), (0, 99)))
		self.l2f = NoSave(ConfigInteger(int(sets[11]), (0, 99)))

		Screen.__init__(self, session)
		self.skinName = "timFS_setDisplay"
		self.refresh()
		self.onChangedEntry = []
		self["titel"] = Label("timFS - " + _("Display Settings"))
		self["pic_red"] = Pixmap()
		self["pic_green"] = Pixmap()
		self["label_green"] = Label(_("Save"))
		self["label_red"] = Label(_("Exit"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
			"ok": self.saveConfig,
			"cancel": self.exit,
			"red": self.exit,
			"green": self.saveConfig
		}, -1)
		ConfigListScreen.__init__(self, self.liste, on_change=self.reloadList)
		self.reloadList()

	def refresh(self):
		timDisplConfigList = []
		timDisplConfigList.extend((
		getConfigListEntry(_("Number of lines:"), self.zeilen),
		getConfigListEntry(_("Scroll-Speed:"), self.scroll_speed),
		getConfigListEntry(_("Display-Len:"), self.len),
		getConfigListEntry(_("Distance from the left:"), self.hp),
		getConfigListEntry(" ",),))
		timDisplConfigList.extend((
			getConfigListEntry(_("Line") + " 1: " + _("Text"), self.l1t),
			getConfigListEntry(_("Line") + " 1: " + _("Distance from the top"), self.l1p),
			getConfigListEntry(_("Line") + " 1: " + _("height"), self.l1h),
			getConfigListEntry(_("Line") + " 1: " + _("Font-Size"), self.l1f),
			getConfigListEntry(" ",),
		))
		if self.zeilen.value > 1:
			timDisplConfigList.extend((
				getConfigListEntry(_("Line") + " 2: " + _("Text"), self.l2t),
				getConfigListEntry(_("Line") + " 2: " + _("Distance from the top"), self.l2p),
				getConfigListEntry(_("Line") + " 2: " + _("height"), self.l2h),
				getConfigListEntry(_("Line") + " 2: " + _("Font-Size"), self.l2f),
			))
		else:
			self.l1t.value = "name"
			self.liste = timDisplConfigList

	def reloadList(self):
		self.refresh()
		self["config"].setList(self.liste)

	def saveConfig(self):
		save_list = ""
		num = 0
		for x in self["config"].list:
			if len(x) > 1:
				num += 1
				if len(save_list):
					save_list = save_list + ","
				save_list = save_list + str('"' + x[1] + '"'.value)
		config.plugins.timFS.display.value = save_list
		config.plugins.timFS.display.save()
		self.close()

	def exit(self):
		self.close()


class timFS(Screen, HelpableScreen):
	def __init__(self, session, liste, eigenlist, gruplist):
		self.plugin_path = plugin_path
		self.session = session
		self.pluginlist_old = liste
		self.pluginlist_old.extend(eigenlist)
		self.font_size = config.plugins.timFS.fontsize.value
		self.group = _("main group")
		self.grup_ind = 0
		self.dump_list = []
		self.grouplist = []
		for x in gruplist:
			self.grouplist.append((x, x))

		with open("/usr/lib/enigma2/python/Plugins/Extensions/timFS/skin/timFS.xml") as tmpskin:
			self.skin = tmpskin.read()
		HelpableScreen.__init__(self)
		Screen.__init__(self, session)
		self.skinName = "timFS"
		self["titel"] = Label("timFS - " + _("The individual menu:") + " " * 10 + self.group + " " * 20)
		self["tim_list"] = List(self.dump_list)
		self["group_list"] = List(self.grouplist)
		self["timfsKeyActions"] = HelpableActionMap(self, "timfsKeyActions",
			{
			"up": self.up,
			"down": self.down,
			"right": self.right,
			"left": self.left,
			"cancel": self.exit,
			"ok": self.ok,
			"info": (self.about, _("about")),
			"nextBouquet": (self.cup, _("Next group")),
			"prevBouquet": (self.cdown, _("Previous group")),
			"menu": (self.timFS_config, _("Settings")),
			}, -1)
		self["numberActions"] = NumberActionMap(["NumberActions"],
			{
			"0": self.keyNumberGlobal,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			}, -1)
		self.onChangedEntry = []
		self["tim_list"].onSelectionChanged.append(self.selectionChanged)
		self.onLayoutFinish.append(self.run)

	def keyNumberGlobal(self, number):
		if number is not None:
			try:
				if int(number) < 10 and len(self.dump_list) >= (number + 1):
					self["tim_list"].setIndex(number)
					self.ok()
			except Exception:
				pass

	def createSummary(self):
		return timFSdisplay

	def selectionChanged(self):
		if len(config.plugins.timFS.display.value.split(",")) > 7 and "name" in config.plugins.timFS.display.value.split(","):
			cur = self["tim_list"].getCurrent()
			txt = ""
			if cur:
				if isinstance(cur[0], basestring):
					txt = str(cur[0])
				else:
					txt = cur[0][0]
				for cb in self.onChangedEntry:
					cb(self.group, txt)

	def right(self):
		self["tim_list"].pageDown()

	def left(self):
		self["tim_list"].pageUp()

	def up(self):
		self["tim_list"].up()

	def down(self):
		self["tim_list"].down()

	def run(self):
		self.dump_list = []
		l1 = []
		for each in self.pluginlist_old:
			(plugin_start, name, hits, hide, sort, group, descrip, art, imp, run) = each
			if each[5] == self.group and int(each[3]) == 0:
				if descrip == "":
					descrip = name
				l1.append([descrip, name, group, plugin_start, hits, sort, art, imp, run, ""])
			if config.plugins.timFS.hits.value == "1" or config.plugins.timFS.hits.value == "4":
				l1.sort(key=lambda x: -int(x[4]))
			elif config.plugins.timFS.hits.value == "2" or config.plugins.timFS.hits.value == "5":
				l1.sort(key=lambda x: int(x[5]))
			else:
				l1.sort(key=lambda p: p[0].lower())
			num = 0
		for x in l1:
			if num < 10:
				x[9] = str(num)
			num += 1
			self.dump_list.append(tuple(x))
		self["group_list"].setList(self.grouplist)
		self["titel"].setText("timFS - " + _("The individual menu:") + " " * 10 + self.group + " " * 20)
		self["tim_list"].setList(self.dump_list)
		self["group_list"].setIndex(self.grup_ind)
		if int(self.font_size) > 22:
			self["group_list"].style = str(self.font_size)
			self["tim_list"].style = str(self.font_size)
		self["tim_list"].setIndex(0)

	def cdown(self):
		sec_index = self.grouplist.index((self.group, self.group)) - 1
		if sec_index < 0:
			sec_index = len(self.grouplist) - 1
		self.group = self.grouplist[sec_index][0]
		self.grup_ind = sec_index
		self.run()

	def cup(self):
		sec_index = self.grouplist.index((self.group, self.group)) + 1
		if sec_index > len(self.grouplist) - 1:
			sec_index = 0
		self.group = self.grouplist[sec_index][0]
		self.grup_ind = sec_index
		self.run()

	def timFS_config(self):
		self.session.openWithCallback(self.reload, timFS_config, plugin_path)

	def reload(self):
		self.close(self.session, "restart")

	def ok(self):
		cur = self["tim_list"].getCurrent()
		if cur:
			write_config(self.pluginlist_old, [], self.grouplist, cur[1], 1)
			param = None
			if int(cur[6]) == 1:
				try:
					t = "from %s import %s" % (cur[7], cur[8])
					exec(t)
					t2 = "self.session.open(" + cur[8] + ")"
					exec(t2)
					if config.plugins.timFS.close1.value:
						self.exit()
				except Exception:
					pass
			else:
				if "Grafischer Multi-EPG" in str(cur[1]):
					param = InfoBar.instance.servicelist
				elif "Serien-Marker" in str(cur[1]):
					param = InfoBar.instance.servicelist
				elif cur[1] == _("Movie archive"):
					param = "aufnahmen"
				if config.plugins.timFS.close1.value:
					self.close(self.session, cur[3], param)
				else:
					if param:
						run = cur[3](self.session, InfoBar.instance.servicelist)  # noqa F841
					else:
						cur[3](self.session)

	def about(self):
		txt = "timFS - the individual menu - Version " + str(version) + "\n"
		txt += "inspired by OpenPanel, MultiQuickbutton and NaviBar\n"
		txt += "coded by shadowrider\n"
		txt += "www.fs-plugins.de"
		self.session.open(MessageBox, txt, type=MessageBox.TYPE_INFO,)

	def exit(self):
		self.close(self.session, "exit")


def closen(session=None, result=None, param=None):
	if session:
		if str(result) == "restart":
			try:
				InfoBar.Original_showExtensionSelection = InfoBar.showExtensionSelection
				InfoBar.showExtensionSelection = start
				InfoBar.instance.showExtensionSelection()
				InfoBar.showExtensionSelection = InfoBar.Original_showExtensionSelection
			except Exception:
				pass
		elif str(result) == "exit":
			pass
		else:
			try:
				if param:
					if param == "aufnahmen":
						InfoBar.showMovies(InfoBar.instance)
					else:
						result(session, param)
				else:
					result(session)
			except Exception:
				pass


def start(self):
		pluginlist = []
		write_new = 0
		names = ["plugin", _("DeviceManager").lower(), _("AtileHD Setup"), _("AutoShutDown Setup"), _("Skinselector").lower(), _("Video Fine-Tuning").lower(),
			_("Videomode-K").lower(), _("Remote channel stream converter").lower(), _("SecondInfoBar").lower(), _("Wireless LAN Setup").lower()]
		pluginlist1 = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_MENU, PluginDescriptor.WHERE_EVENTINFO])
		pluginlist1.sort(key=lambda p: p.name.lower())
		mv_str = _("Movie archive")
		for plugin in pluginlist1:
			if plugin.name.lower() in names:
				pass
			else:
				pluginlist.append((plugin, plugin.name))
				names.append(plugin.name.lower())
		if mv_str.lower() not in names:
			try:
				from Screens.MovieSelection import MovieSelection  # noqa F401
				pluginlist.append(("MovieSelection", mv_str))
				names.append(mv_str.lower())
			except Exception:
				pass
		if not fileExists(conf_path) or (fileExists(conf_path) and os.path.getsize(conf_path) == 0):
			nl = []
			el = []
			gl = []
			gl.append(_("main group"))
			write_new = 1
			write_config(nl, el, gl)

		p_list = []
		listen = read_config()
		new_list = []
		if len(listen[0]) != len(pluginlist):
			write_new = 1
		#f2=open("/tmp/tim3","w")
		for plugin in pluginlist:
			#f2.write(str(plugin)+"\n")
			try:
				(plugin_start, plugin_name) = plugin
				#f2.write(str(plugin_name)+"\n")
				writed = 0
				for line in listen[0]:
					if line[0].lower() == str(plugin_name).strip().lower():
						writed = 1
						if write_new == 1:
							new_list.append(("", line[0], line[1], line[2], line[3], line[4], line[5], line[6], "", ""))
						p_list.append((plugin_start, line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8]))
						break
				if writed == 0:
					if str(plugin_start) == "MovieSelection":
						p_list.append((plugin_name, plugin_name, "0", "0", "99", _("main group"), _("Movie archive"), 0, "", ""))
					else:
						p_list.append((plugin_start, plugin_name, "0", "0", "99", _("main group"), "", 0, "", ""))
					if write_new == 1:
						if str(plugin_start) == "MovieSelection":
							new_list.append(("", plugin_name, "0", "0", "99", _("main group"), _("Movie archive"), 0, "", ""))
						else:
							new_list.append(("", plugin_name, "0", "0", "99", _("main group"), "", 0, "", ""))

			except Exception:
				pass
			#f2.close()

		if write_new == 1:
			write_config(new_list, listen[1], listen[2], None, None)
		self.session.openWithCallback(closen, timFS, p_list, listen[1], listen[2])


def read_config():
	pluglist = []
	eigenlist = []
	gruplist = []
	config_read = open(conf_path, "r")
	config_read_zeilen = config_read.readlines()
	config_read.close()
	for line in config_read_zeilen:
		if not line.strip().startswith("#"):
			read1 = []
			read = line.replace(r"\,", ";").split(",")
			for x in read:
				read1.append(str(x).strip())
			if read1:
				if read1[0] == "0":
					pluglist.append((read1[1].replace(";", ","), read1[2], read1[3], read1[4], read1[5], read1[6], 0, "", ""))
				elif read1[0] == "1":
					eigenlist.append((None, read1[1].replace(";", ","), read1[2], read1[3], read1[4], read1[5], read1[6], int(read1[0]), read1[7], read1[8]))
				elif read1[0] == "2":
					gruplist.append(read1[1])
	return (pluglist, eigenlist, gruplist)


def write_config(pluglist=None, eigenlist=None, gruplist=None, akt=None, double=None):
	config_tmp = open(conf_path, "w")
	config_tmp.write('# config settings for plugin timFS -the individual menu):\n')
	config_tmp.write('# art: "0" =auto-read, "1" =individual, "2" =group\n')
	config_tmp.write('# auto-read: art, name, hits, hide, sort, group\n')
	config_tmp.write('# individual, sample for network (from Screens.NetworkSetup import NetworkAdapterSelection)\n#   1,Netzwerk,0,0,99,' + _("main group") + ',Netzwerk,Screens.NetworkSetup,NetworkAdapterSelection\n')
	config_tmp.write('# group (order as this list): 2,name \n')
	if len(gruplist):
		for x in gruplist:
			if double:
				config_tmp.write('2,%s\n' % x[0])
			else:
				config_tmp.write('2,%s\n' % x)
	if len(eigenlist):
		for x in eigenlist:
			hits = int(x[2])
			if akt and akt == x[1]:
				hits += 1
			config_tmp.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (x[7], x[1].replace(",", r"\,"), hits, x[3], x[4], x[5], x[6], x[8].replace(",", r"\,"), x[9]))
	if len(pluglist):
		for x in pluglist:
			hits = int(x[2])
			if akt and akt == x[1]:
				hits += 1
			if len(x[8]):
				config_tmp.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (x[7], x[1].replace(",", r"\,"), hits, x[3], x[4], x[5], x[6], x[8].replace(",", r"\,"), x[9]))
			else:
				config_tmp.write('%s,%s,%s,%s,%s,%s,%s\n' % (x[7], x[1].replace(",", r"\,"), hits, x[3], x[4], x[5], x[6]))
	config_tmp.close()


class timFSdisplay(Screen):

	def __init__(self, session, parent):
		skincontent = ""
		sets = config.plugins.timFS.display.value.split(",")
		self.scroll = sets[1]
		num = 4
		self.label_list = []
		while num < len(sets):
			self.label_list.append(sets[num].strip())
			num += 4
		num = 4
		for x in self.label_list:
			skincontent += "<widget name=\"" + x + "\" position=\"" + str(sets[3]) + "," + str(sets[num + 1]) + "\" size=\"" + str(sets[2]) + "," + str(sets[num + 2]) + "\"  font=\"Regular;" + str(sets[num + 3]) + "\" noWrap=\"1\" />  "
			num += 4
		self.skin = "<screen name=\"timFSdisplay\" position=\"0,0\" size=\"" + str(sets[2]) + ",300\" >" + skincontent + "</screen>"
		Screen.__init__(self, session, parent=parent)
		for x in self.label_list:
			if len(x):
				self[x] = Label()
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)
		self.display_text = "timFS"
		self.dp_text = "timFS"
		self.scrollTimer = eTimer()
		self.scrollTimer.timeout.get().append(self.scroll_Timeout)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, group="timFS", name=""):
		if self.scrollTimer and self.scrollTimer.isActive():
			self.scrollTimer.stop()
		self.scroll_Timeout()
		for x in self.label_list:
			try:
				self[x].text = group if x == "group" else name
			except Exception:
				pass
		self.dp_text = name
		self.display_text = name

	def scroll_Timeout(self):
		if int(self.scroll) > 0:
			self["name"].text = self.dp_text
			self.dp_text = self.dp_text[1:len(self.dp_text)]
			if len(self.dp_text) < 20:
				self.dp_text = self.dp_text + " *** " + self.display_text
			self.scrollTimer.start(int(self.scroll) * 100)


def main(session, **kwargs):
	InfoBar.Original_showExtensionSelection = InfoBar.showExtensionSelection
	InfoBar.showExtensionSelection = start
	InfoBar.instance.showExtensionSelection()
	InfoBar.showExtensionSelection = InfoBar.Original_showExtensionSelection


def runPlugin(self, plugin):
	if isinstance(InfoBar.instance, InfoBarChannelSelection):
		plugin(session=self.session, servicelist=InfoBar.instance.servicelist)
	else:
		plugin(session=self.session)


def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("timFS", main, "timFS", None)]
	return []


def Plugins(path, **kwargs):
	global plugin_path
	plugin_path = path
	list = [PluginDescriptor(name="timFS", description=_("The individual menu"), where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=main, icon="timFS.png")]
	if config.plugins.timFS.hauptmenu.value:
		list.append(PluginDescriptor(name="timFS", where=[PluginDescriptor.WHERE_MENU], fnc=menu))
	return list
