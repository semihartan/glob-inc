## glob-inc (**Glob**ally **inc**lude)

glob-inc is a simple utility to patch the necessary MSBuild files to add third-party libraries to all C/C++ projects on Visual Studio.

This is my personal preference when working with `C/C++` on Visual Studio. I've created a directory somewhere named `3rdparty` that has subdirectories for include files and binary library files. A typical structure for this kind of directory is as follows.

```
--> 3rdparty
  |--> include     - All include files go in here.
  |--> lib         - All library files go in here
     |--> x86      - All library files compiled for x86-32 go here.
     |--> x64      - All library files compiled for x86-64 go here.
     |--> arm      - All library files compiled for arm32 go here.
     |--> arm64    - All library files compiled for arm64 go here.
```

This is a mostly preferred hierarchical convention, so I stick to this, and recommend it to you as well through the script. However, you might want to follow your own convention. If this is the case, change it in the script.

## Usage

The usage is very simple. There is no any positional arguments. You can run it as-is. 

```
> glob-inc
```

However, it has several useful arguments that you may want to use. 

You can specify a root directory that contains include and library files with the option `--path`. If you don't specify it, it defaults to `C:\3rdparty\`.

```
> glob-inc --path "Your path"
```

It can create the directories if they don't exist. In order for that, you should specify the optional flag `-c`. 

```
> glob-inc --path "Your path" -c
```

You can perform the patching for several architectures, namely `x86` (both `x86-32` and `x86-64`), `x86-32`, `arm` (both `arm32` and `arm64`), `arm32`, `arm64`. It will patch the files and create the directories only for the speficied architecture(s).

```
> glob-inc --path "Your path" -c -p x86
```

## Note
Visual Studio can reset the MSBuild files that's been patched when you update it. Therefore, run this script everytime you update Visual Studio. 