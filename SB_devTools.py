bl_info = {
    "name": "dev tools",
    "description": "Add tool to help developpement",
    "author": "Samuel Bernou",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "Text editor > toolbar",
    "warning": "",
    "wiki_url": "https://github.com/Pullusb/devTools",
    "category": "Text Editor" }

import bpy
import os
import re
import difflib
import subprocess
from sys import platform

###---UTILITY funcs

def openFolder(folderpath):
    """
    open the folder at the path given
    with cmd relative to user's OS
    """
    myOS = platform
    if myOS.startswith(('linux','freebsd')):
        cmd = 'xdg-open'
    elif myOS.startswith('win'):
        cmd = 'explorer'
        if not folderpath:
            return('/')
    else:
        cmd = 'open'

    if not folderpath:
        return('//')

    fullcmd = [cmd, folderpath]
    print(fullcmd)
    subprocess.Popen(fullcmd)
    return ' '.join(fullcmd)#back to string to print


def openFile(filepath):
    '''open the file at the path given with cmd relative to user's OS'''
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[__name__].preferences
    editor = addon_prefs.external_editor

    if not filepath:
        return('No file path !')

    if editor:
        cmd = editor
    else:
        myOS = platform
        if myOS.startswith('linux') or myOS.startswith('freebsd'):# linux
            cmd = 'xdg-open'
        elif myOS.startswith('win'):# Windows
            cmd = 'start'
        else:# OS X
            cmd = 'open'

    mess = cmd + ' ' + filepath
    fullcmd = [cmd,filepath]

    print(fullcmd)

    try:
        subprocess.Popen(fullcmd)
    except:
        import traceback
        traceback.print_exc()
        mess = 'Text editor not found ' + mess
        return {'CANCELLED'}


    return mess

def copySelected():
    '''Copy selected Text'''

    bpy.ops.text.copy()
    clip = bpy.context.window_manager.clipboard
    return (clip)


def print_string_variable(clip,linum=''):
    if linum:
        line = 'print(":l {1}:{0}", {0})#Dbg'.format(clip, str(linum) )
    else:
        line = 'print("{0}", {0})#Dbg'.format(clip)
    #'print("'+ clip + '", ' + clip + ')#Dbg'
    return (line)


def Fixindentation(Loaded_text, charPos):
    '''take text and return it indented according to cursor position'''

    FormattedText = Loaded_text
    # print("FormattedText", FormattedText)#Dbg
    if charPos > 0:
        textLines = Loaded_text.split('\n')
        if not len(textLines) == 1:
            #print("indent subsequent lines")
            indentedLines = []
            indentedLines.append(textLines[0])
            for line in textLines[1:]:
                indentedLines.append(' '*charPos + line)

            FormattedText = '\n'.join(indentedLines)
        else:
            FormattedText = ' '*charPos + FormattedText

    return (FormattedText)

def re_split_line(line):
    '''
    take a line string and return a 3 element list:
    [ heading spaces (id any), '# '(if any), rest ot the string ]
    '''
    r = re.search(r'^(\s*)(#*\s?)(.*)', line)
    return ( [r.group(1), r.group(2), r.group(3)] )

def get_text(context):
    #get current text
    text = getattr(bpy.context.space_data, "text", None)

    #context override for the ops.text.insert() function
    override = {'window': context.window,
                'area'  : context.area,
                'region': context.region,
                'space': context.space_data,
                'edit_text' : text
                }
    return(text, override)


###---TASKS

class DEV_OT_simplePrint(bpy.types.Operator):
    bl_idname = "devtools.simple_print"
    bl_label = "Simple print text"
    bl_description = "Add a new line with debug print of selected text\n(replace clipboard)"
    bl_options = {"REGISTER"}

    bpy.types.Scene.line_in_debug_print = bpy.props.BoolProperty(
    name="include line num", description='include line number in print', default=False)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        #get current text object
        text, override = get_text(context)

        #create debug print from variable selection
        charPos = text.current_character
        clip = copySelected()
        debugPrint = 'print({0})'.format(clip)#'print({0})#Dbg'

        ###On a new line
        # heading_spaces = re.search('^(\s*).*', text.current_line.body).group(1)
        # new = Fixindentation(debugPrint, len(heading_spaces))#to insert at selection level : charPos
        # bpy.ops.text.move(override, type='LINE_END')
        # bpy.ops.text.insert(override, text= '\n'+new)

        ### In place
        bpy.ops.text.insert(override, text=debugPrint)
        return {"FINISHED"}

class DEV_OT_quote(bpy.types.Operator):
    bl_idname = "devtools.quote"
    bl_label = "quote text"
    bl_description = "quote text"
    bl_options = {"REGISTER"}

    bpy.types.Scene.line_in_debug_print = bpy.props.BoolProperty(
    name="include line num", description='include line number in print', default=False)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        charPos = text.current_character
        clip = copySelected()
        if '"' in clip:
            debugPrint = "'{0}'".format(clip)#'print({0})#Dbg'
        else:
            debugPrint = '"{0}"'.format(clip)

        ###On a new line
        # heading_spaces = re.search('^(\s*).*', text.current_line.body).group(1)
        # new = Fixindentation(debugPrint, len(heading_spaces))#to insert at selection level : charPos
        # bpy.ops.text.move(override, type='LINE_END')
        # bpy.ops.text.insert(override, text= '\n'+new)

        ### In place
        bpy.ops.text.insert(override, text=debugPrint)
        return {"FINISHED"}


class DEV_OT_insert_import(bpy.types.Operator):
    bl_idname = "devtools.insert_import"
    bl_label = "insert import text"
    bl_description = "import text"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        #create new text-block if not any
        if text == None:
            text = bpy.data.texts.new('Text')
            context.space_data.text = text
            text, override = get_text(context)#reget_override
        charPos = text.current_character
        #clip = copySelected()
        import_text = "# coding: utf-8\nimport bpy\nimport os\nfrom os import listdir\nfrom os.path import join, dirname, basename, exists, isfile, isdir, splitext\nimport re, fnmatch, glob\nfrom mathutils import Vector, Matrix\nfrom math import radians, degrees\nC = bpy.context\nD = bpy.data\nscene = C.scene\n"

        bpy.ops.text.insert(override, text=import_text)
        return {"FINISHED"}



class DEV_OT_debugPrintVariable(bpy.types.Operator):
    bl_idname = "devtools.debug_print_variable"
    bl_label = "Debug Print Variable"
    bl_description = "add a new line with debug print of selected text\n(replace clipboard)"
    bl_options = {"REGISTER"}

    bpy.types.Scene.line_in_debug_print = bpy.props.BoolProperty(
    name="include line num", description='include line number in print', default=False)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        #get current text object
        text, override = get_text(context)

        #create debug print from variable selection
        charPos = text.current_character
        clip = copySelected()
        if bpy.context.scene.line_in_debug_print:
            debugPrint = print_string_variable(clip, linum=text.current_line_index+1)
        else:
            debugPrint = print_string_variable(clip)

        #send charpos at current indentation (number of whitespace)
        heading_spaces = re.search('^(\s*).*', text.current_line.body).group(1)

        new = Fixindentation(debugPrint, len(heading_spaces))#to insert at selection level : charPos

        #got to end of line,
        ### > current_character" from "Text" is read-only
        #text.current_character = len(text.lines[text.current_line_index].body)
        bpy.ops.text.move(override, type='LINE_END')

        #put a return and paste with indentation
        bpy.ops.text.insert(override, text= '\n'+new)
        return {"FINISHED"}



class DEV_OT_disableAllDebugPrint(bpy.types.Operator):
    bl_idname = "devtools.disable_all_debug_print"
    bl_label = "Disable all debug print"
    bl_description = "comment all lines finishing with '#Dbg'"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        count = 0
        for i, lineOb in enumerate(text.lines):
            if lineOb.body.endswith('#Dbg'):#detect debug lines
                line = lineOb.body
                splitline = re_split_line(line)
                if not splitline[1]: #detect comment
                    count += 1
                    lineOb.body = splitline[0] + '# ' +  splitline[2]
                    print ('line {} commented'.format(i))
        if count:
            mess = str(count) + ' lines commented'
        else:
            mess = 'No line commented'
        self.report({'INFO'}, mess)
        return {"FINISHED"}



class DEV_OT_enableAllDebugPrint(bpy.types.Operator):
    bl_idname = "devtools.enable_all_debug_print"
    bl_label = "Enable all debug print"
    bl_description = "uncomment all lines finishing wih '#Dbg'"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        count = 0
        for i, lineOb in enumerate(text.lines):
            if lineOb.body.endswith('#Dbg'):#detect debug lines
                line = lineOb.body
                splitline = re_split_line(line)
                if splitline[1]: #detect comment
                    count += 1
                    lineOb.body = splitline[0] + splitline[2]
                    print ('line {} uncommented'.format(i))
        if count:
            mess = str(count) + ' lines uncommented'
        else:
            mess = 'No line uncommented'
        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_expandShortcutName(bpy.types.Operator):
    bl_idname = "devtools.expand_shortcut_name"
    bl_label = "Expand text shortcuts"
    bl_description = "replace 'C.etc' by 'bpy.context.etc'\n and 'D.etc' by 'bpy.data.etc'"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        rxc = re.compile(r'C(?=\.)')#(?<=[^A-Za-z0-9\.])C(?=\.)
        rxd = re.compile(r'D(?=\.)')#(?<=[^A-Za-z0-9\.])D(?=\.)
        for line in text.lines:
            line.body = rxc.sub('bpy.context', line.body)
            line.body = rxd.sub('bpy.data', line.body)

        return {"FINISHED"}


class DEV_OT_updateDebugLinum(bpy.types.Operator):
    bl_idname = "devtools.update_debug_linum"
    bl_label = "Update_debug linum"
    bl_description = "update number in debug prints that are using linum print"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        relinum = re.compile(r'(print\(\":l) \d+(:)')
        renum = re.compile(r'print\(\":l (\d+):')
        #match element: .*print:l 12:.*
        ct = 0
        for i, line in enumerate(text.lines):
            match = relinum.search(line.body)
            if match:
                newnum = str(i)
                num = renum.search(line.body).group(1)
                if newnum != num:
                    #print('linum updated at line:', i)
                    pattern = r'\1 {}\2'.format(newnum)
                    line.body = relinum.sub(pattern, line.body)
                    ct+=1
        if ct:
            mess = str(ct) + ' print updated'
            self.report({'INFO'}, mess)
        else:
            self.report({'INFO'}, 'All good')

        return {"FINISHED"}

class DEV_OT_writeClassesTuple(bpy.types.Operator):
    bl_idname = "devtools.write_classes_tuple"
    bl_label = "Write classes tuple"
    bl_description = "Write a classes tuple containing all class in text"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)

        block = 'classes = (\n'
        for line in text.lines:
            if line.body.startswith('class '):
                block += '{},\n'.format(re.search(r'class (.*)\(.*', line.body).group(1))
        block += ')'
        text.write(block)

        return {"FINISHED"}

class DEV_OT_textDiff(bpy.types.Operator):
    bl_idname = "devtools.diff_internal_external"
    bl_label = "Text diff external"
    bl_description = "print dif in console with the difference between current internal file and external saved version"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        if text.filepath:
            if text.is_dirty or text.is_modified:
                print(8*'- ')

                internal = [l.body for l in text.lines]#get line from internal
                fp = text.filepath
                #print("text-filepath", fp)#Dbg
                fp = bpy.path.abspath(fp)
                #print("abs_path", fp)#Dbg
                with open(fp, 'r') as fd:
                    ext = fd.read().splitlines()

                changes = difflib.context_diff(internal,ext,fromfile='local', tofile='external')
                #changes = difflib.unified_diff(internal,ext)

                #print(linecount)
                print (str((len(internal))) + ' internal\n' + str((len(ext))) + ' external\n')

                if [c for c in changes]:#if diff generator  is not empty
                    for change in changes:
                        if not change.startswith(' '):
                            print(change)
                    mess = 'look the diff in console'
                else:
                    mess = 'no diff detected'
            else:
                mess = 'file is synced'

        else:
            mess = 'text is internal only'

        self.report({'INFO'}, mess)
        return {"FINISHED"}

class DEV_OT_openExternalEditor(bpy.types.Operator):
    bl_idname = "devtools.open_in_default_editor"
    bl_label = "Open externally"
    bl_description = "Open in external default program or software specified in addon preferences"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        if text.filepath:#not necessary, button masked if no external data
            mess = openFile(text.filepath)
        else:
            mess = 'Text is internal only'

        self.report({'INFO'}, mess)
        return {"FINISHED"}

class DEV_OT_openScriptFolder(bpy.types.Operator):
    bl_idname = "devtools.open_script_folder"
    bl_label = "Open folder"
    bl_description = "Open text folder in OS browser"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        if text.filepath:
            mess = openFolder(os.path.dirname(text.filepath))
        else:
            mess = 'Text is internal only'

        self.report({'INFO'}, mess)
        return {"FINISHED"}

class DEV_OT_printResourcesPaths(bpy.types.Operator):
    bl_idname = "devtools.print_resources_path"
    bl_label = "print ressources filepath"
    bl_description = "Print usefull resources filepath in console"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        linesep = 10*'-'
        print(linesep)
        print('Ressources path'.upper())
        print(linesep)
        print('Local default installed addons (release):\n{}\n'.format(os.path.join(bpy.utils.resource_path('LOCAL') , 'scripts', 'addons')) )
        print('Local user addon source (usually appdata roaming)\nWhere it goes when you do an "install from file":\n{}\n'.format(bpy.utils.user_resource('SCRIPTS', "addons")) )

        preferences = bpy.context.preferences
        external_script_dir = preferences.filepaths.script_directory
        if external_script_dir and len(external_script_dir) > 2:
            print('external scripts:\n{}\n'.format(external_script_dir) )

        #config
        print('config path:\n{}\n'.format(bpy.utils.user_resource('CONFIG')) )
        #binary path
        print('binary path:\n{}\n'.format(bpy.app.binary_path) )

        print(linesep)

        mess = 'Look in console'
        self.report({'INFO'}, mess)
        return {"FINISHED"}


class DEV_OT_openFilepath(bpy.types.Operator):
    bl_idname = "devtools.open_filepath"
    bl_label = "Open folder at given filepath"
    bl_description = "Open given filepath in OS browser"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    fp : bpy.props.StringProperty()

    def execute(self, context):
        filepath = self.fp
        if not filepath:
            print('Problem ! No filepath was receieved in operator')
            return {"CANCELLED"}

        if not os.path.exists(filepath):
            print('filepath not found', filepath)
            return {"CANCELLED"}

        mess = openFolder(filepath)

        self.report({'INFO'}, mess)
        return {"FINISHED"}

class DEV_OT_insertDate(bpy.types.Operator):
    bl_idname = "devtools.insert_date"
    bl_label = "Insert date string"
    bl_description = "Insert date at current position (reclick to add details)"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def execute(self, context):
        text, override = get_text(context)
        #create new text-block if not any
        if text == None:
            text = bpy.data.texts.new('Text')
            context.space_data.text = text
            text, override = get_text(context)#reget_override

        from time import strftime
        content = strftime('%Y/%m/%d')
        #if current_line
        print( strftime('---date---\n%c\n%A %B') )
        if re.search(r'\d{4}/\d{2}/\d{2}.*\d{2}:\d{2}:\d{2}.*[A-Z]{1}[a-z]{2}', text.current_line.body):#full
            self.report({'ERROR'}, 'detected as full date')#or just pass...
            return {"CANCELLED"}
        elif re.search(r'\d{4}/\d{2}/\d{2}.*\d{2}:\d{2}:\d{2}', text.current_line.body):
            content = strftime(' %a')#abreviated month
        elif re.search(r'\d{4}/\d{2}/\d{2}', text.current_line.body):
            content = strftime(' %H:%M:%S')#add hours
        else:
            content = strftime('%Y/%m/%d')#date

        ## print detailed version -> %c: full detailed, %A %B full month and day
        bpy.ops.text.insert(override, text=content)
        return {"FINISHED"}

class DEV_OT_blenderInfo(bpy.types.Operator):
    bl_idname = "devtools.blender_info"
    bl_label = "Blender infos"
    bl_description = "Insert blender release info (Date, Hash, branch).\nUsefull for bug report"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'TEXT_EDITOR'

    def strip_b_str(self, s):
        if str(s).startswith("b'"):
            return str(s)[2:-1]
        else:
            return s

    def execute(self, context):
        text, override = get_text(context)
        if text == None:
            text = bpy.data.texts.new('Text')
            context.space_data.text = text
            text, override = get_text(context)

        build_text = "Date : {}\nHash : {}\nBranch : {}\nVersion: {}".format(\
        self.strip_b_str(bpy.app.build_date), self.strip_b_str(bpy.app.build_hash), self.strip_b_str(bpy.app.build_branch), bpy.app.version_string)

        bpy.ops.text.insert(override, text=build_text)

        #print in console
        print('\n---Full build infos---')
        for attr in dir(eval("bpy.app")):
            if attr.startswith('build'):
                print(attr)
                try:
                    value = str(getattr(eval("bpy.app"),attr))
                    print(self.strip_b_str(value) )
                    print()
                except AttributeError:
                    print('! ERROR !\n')

        print('--------\nMinimal infos:\n'+build_text+'\n------\n')
        self.report({'INFO'}, 'Full info Printed in console')
        return {"FINISHED"}

###---PANEL

class DEV_PT_devTools(bpy.types.Panel):
    bl_idname = "DEV_PT_dev_tools"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_category = "Dev"
    bl_label = "Dev Tools"

    def draw(self, context):
        layout = self.layout
        row=layout.row()
        row.prop(context.scene, 'line_in_debug_print')
        row.operator(DEV_OT_updateDebugLinum.bl_idname, text='', icon='FILE_REFRESH')#Update
        layout.operator(DEV_OT_debugPrintVariable.bl_idname)
        layout.separator()
        layout.operator(DEV_OT_disableAllDebugPrint.bl_idname)
        layout.operator(DEV_OT_enableAllDebugPrint.bl_idname)
        layout.separator()

        layout.operator(DEV_OT_writeClassesTuple.bl_idname)
        layout.operator(DEV_OT_expandShortcutName.bl_idname)

        #When text is saved externally draw more option
        text,override = get_text(context)
        if text and text.filepath :#mask button if file is pure internal
            layout.separator()
            layout.operator(DEV_OT_textDiff.bl_idname)
            layout.operator(DEV_OT_openScriptFolder.bl_idname)
            layout.operator(DEV_OT_openExternalEditor.bl_idname)

        layout.label(text='open scripts places')
        row = layout.row()
        #local default installed addons (release)
        row.operator(DEV_OT_openFilepath.bl_idname, text='built-in addons').fp = os.path.join(bpy.utils.resource_path('LOCAL') , 'scripts', 'addons')

        #Local user addon source (usually appdata roaming)\nWhere it goes when you do an 'install from file'
        row.operator(DEV_OT_openFilepath.bl_idname, text='users addons').fp = bpy.utils.user_resource('SCRIPTS', "addons")

        layout = self.layout
        #common script (if specified)
        preferences = bpy.context.preferences
        external_script_dir = preferences.filepaths.script_directory
        if external_script_dir and len(external_script_dir) > 2:
            layout.operator(DEV_OT_openFilepath.bl_idname, text='external scripts folder').fp = external_script_dir

        layout.separator()
        #path printer
        layout.operator(DEV_OT_printResourcesPaths.bl_idname)

        #infos printer
        row = layout.row()
        row.operator(DEV_OT_insertDate.bl_idname, text='Insert date')
        row.operator(DEV_OT_blenderInfo.bl_idname, text='Release infos')

###---PREF PANEL

class DEV_PT_tools_addon_pref(bpy.types.AddonPreferences):
    bl_idname = __name__

    external_editor : bpy.props.StringProperty(
            name="External Editor",
            subtype='FILE_PATH',
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "external_editor")


###---KEYMAP

addon_keymaps = []
def register_keymaps():
    wm = bpy.context.window_manager
    addon = bpy.context.window_manager.keyconfigs.addon
    km = wm.keyconfigs.addon.keymaps.new(name = "Text", space_type = "TEXT_EDITOR")

    kmi = km.keymap_items.new("devtools.simple_print", type = "P", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("devtools.debug_print_variable", type = "P", value = "PRESS", ctrl = True, shift = True)
    kmi = km.keymap_items.new("devtools.quote", type = "L", value = "PRESS", ctrl = True)
    kmi = km.keymap_items.new("devtools.insert_import", type = "I", value = "PRESS", ctrl = True, shift=True)

    addon_keymaps.append(km)

def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


###---REGISTER

classes = (
DEV_OT_simplePrint,
DEV_OT_quote,
DEV_OT_insert_import,
DEV_OT_debugPrintVariable,
DEV_OT_disableAllDebugPrint,
DEV_OT_enableAllDebugPrint,
DEV_OT_expandShortcutName,
DEV_OT_textDiff,
DEV_OT_openExternalEditor,
DEV_OT_openScriptFolder,
DEV_OT_updateDebugLinum,
DEV_OT_writeClassesTuple,
DEV_OT_printResourcesPaths,
DEV_OT_openFilepath,
DEV_OT_insertDate,
DEV_OT_blenderInfo,
DEV_PT_devTools,
DEV_PT_tools_addon_pref,
)


def register():
    if not bpy.app.background:
        for cls in classes:
            bpy.utils.register_class(cls)

        register_keymaps()

def unregister():
    if not bpy.app.background:
        unregister_keymaps()

        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
