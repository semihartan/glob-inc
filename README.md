## glob-inc (**Glob**ally **Inc**lude)

`glob-inc` is a simple utility designed to patch necessary MSBuild files, allowing you to globally include third-party libraries in all C/C++ projects in Visual Studio.

This utility reflects my personal approach to organizing third-party libraries when working with `C/C++` on Visual Studio. I typically create a directory called `3rdparty`, which contains subdirectories for include files and binary libraries. A typical directory structure looks like this:

```
--> 3rdparty
  |--> include     - All include files are stored here.
  |--> lib         - All library files are stored here.
     |--> x86      - Libraries compiled for x86-32 go here.
     |--> x64      - Libraries compiled for x86-64 go here.
     |--> arm      - Libraries compiled for ARM32 go here.
     |--> arm64    - Libraries compiled for ARM64 go here.
```

This hierarchical convention is commonly used, and I recommend it. However, if you prefer a different structure, feel free to modify the script to fit your own convention.

## Usage

Using `glob-inc` is straightforward. It doesn’t require any positional arguments. You can run it as-is with:

```
> glob-inc
```

However, there are several useful options you might want to leverage.

You can specify the root directory containing the include and library files using the `--path` option. If not specified, it defaults to `C:\3rdparty\`.

```
> glob-inc --path "Your path"
```

If the specified directories don’t exist, you can instruct the utility to create them by using the `-c` flag:

```
> glob-inc --path "Your path" -c
```

You can also limit the patching process to specific architectures, such as `all` (all platforms), `x86` (both `x86-32` and `x86-64`), `x86-32`, `arm` (both `arm32` and `arm64`), `arm32`, and `arm64`. The script will then patch the relevant MSBuild files and create the necessary directories for the selected architecture(s).

```
> glob-inc --path "Your path" -c -px86
```

Unpatching can be done using the `-u, --unpatch` option. It unpatches for all the architectures.

```
> glob-inc -u
```

## Note

Visual Studio may reset the patched MSBuild files after an update. Therefore, it's recommended to re-run this script whenever you update Visual Studio.
