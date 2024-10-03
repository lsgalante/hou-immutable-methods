#ifndef _im_utils_
#define _im_utils_

// Iterated Neighbours
int[] im_nbrs(int geo; int pt_in; int depth) {
    int pt_arr[] = array(pt_in);
    int searched[] = array(pt_in);
    int result[] = array(pt_in);
    for(int i = 0; i < depth; i++) {
        int new_pt_arr[] = {};
        foreach(int pt; pt_arr) {
            int nbr_arr[] = neighbours(geo, pt);
            foreach(int nbr; nbr_arr) {
                int idx = find(searched, nbr);
                if(idx < 0) {
                    append(searched, nbr);
                    append(new_pt_arr, nbr);
                    append(result, nbr);
                }
            }
        }
        pt_arr = new_pt_arr;
    }
    return result;
}
int[] im_nbrs(int geo; int pt_arr_in[]; int depth) {
    int pt_arr[] = pt_arr_in;
    int searched[] = pt_arr_in;
    int result[] = pt_arr_in;
    for(int i = 0; i < depth; i++) {
        int new_pt_arr[] = {};
        foreach(int pt; pt_arr) {
            int nbr_arr[] = neighbours(geo, pt);
            foreach(int nbr; nbr_arr) {
                int idx = find(searched, nbr);
                if(idx < 0) {
                    append(searched, nbr);
                    append(new_pt_arr, nbr);
                    append(result, nbr);
                }
            }
        }
        pt_arr = new_pt_arr;
    }
    return result;
}

// neighbours Shortcut
int[] im_nbrs(int geo; int pt) {
    int nbrs[] = neighbours(geo, pt);
    return nbrs;
}

// Neighbours in Group
int[] im_nbrs_in_group(int geo; string group; int pt) {
    int nbrs_0[] = neighbours(geo, pt);
    int nbrs_1[];
    int group_pts[] = expandpointgroup(0, group);
    foreach(int nbr; nbrs_0) {
        int idx = find(group_pts, nbr);
        if(idx >= 0)
            append(nbrs_1, nbr);
    }
    return(nbrs_1);
}

// setpointattrib Shortcut
void im_set_pt_attr(int geo; string attr; int pt; int val) {
    setpointattrib(geo, attr, pt, val);
}
void im_set_pt_attr(int geo; string attr; int pt; int val[]) {
    setpointattrib(geo, attr, pt, val);
}

// setpointgroup Shortcut
void im_set_pt_grp(int geo; string group; int pt; int val) {
    setpointgroup(geo, group, pt, val);
}

// npoints Shortcut
int im_npts(int geo) {
    return(npoints(geo));
}

// Float to String
string im_ftoa(const float f; const int decimal_places) {
    return sprintf("%.*g", decimal_places + (int)log10(abs(f)) + (abs(f) >= 1.0), f);
}
string im_ftoa(const float f) {
    return im_ftoa(f, 3);
}

// Binary Search
float im_bin_search(const int arr[], target_val; export int success) {
    success = 0;
    int ct = len(arr);
    if(ct == 0)
        return -1.0;
    int l = 0;
    int r = ct - 1;
    int m = -1;

    while(l <= r) {
        m = (l + r) / 2;
        if(arr[m] < target_val)
            l = m + 1;
        else if(arr[m] > target_val)
            r = m - 1;
        else {
            success = 1;
            break;
        }
    }
    // Only happens when the left index is 1 less than the right
    // index and the target value is between the two values
    if(l > r)
        m = r;
    // If the target value is greater than a few duplicated values
    // but less than the next value, the middle index will always
    // move to the last of the duplicates
    float idx = m;
    if(!success) {
        if(target_val < arr[0] || target_val > arr[ct - 1])
            idx = -1.0;
        else if(m + 1 < ct)
            // In VEX division by zero returns zero.
            idx += float(target_val - arr[m]) / (arr[m + 1] - arr[m]);
    }
    return idx;
}
float im_bin_search(const float arr[], target_val; export int success) {
    success = 0;
    int ct = len(arr);
    if(ct == 0)
        return -1.0;
    int l = 0;
    int r = ct - 1;
    int m = -1;
    // Forces the target value to have the same floating-point precision as the array elements
    float target_val_safe = set(target_val, 0)[0];

    while (l <= r) {
        m = (l + r) / 2;
        if(arr[m] < target_val_safe)
            l = m + 1;
        else if(arr[m] > target_val_safe)
            r = m - 1;
        else {
            success = 1;
            break;
        }
    }
    // Only happens when the left index is 1 less than the right
    // index and the target value is between the two values
    if(l > r)
        m = r;
    // If the target value is greater than a few duplicated values
    // but less than the next value, the middle index will always
    // move to the last of the duplicates
    float idx = m;
    if(!success) {
        if(target_val_safe < arr[0] || target_val_safe > arr[ct - 1])
            idx = -1.0;
        else if(m + 1 < ct)
            // In VEX division by zero returns zero.
            idx += float(target_val_safe - arr[m]) / (arr[m + 1] - arr[m]);
    }
    return idx;
}
int im_bin_search(const string arr[], target_val; export int success) {
    success = 0;
    int ct = len(arr);
    if(ct == 0)
        return -1;
    int l = 0;
    int r = ct - 1;
    int m = -1;

    while(l <= r) {
        m = (l + r) / 2;
        if(arr[m] < target_val)
            l = m + 1;
        else if(arr[m] > target_val)
            r = m - 1;
        else {
            success = 1;
            break;
        }
    }
    // Only happens when the left index is 1 less than the right
    // index and the target value is between the two values
    if(l > r)
        m = r;
    // If the target value is greater than a few duplicated values
    // but less than the next value, the middle index will always
    // move to the last of the duplicates
    int idx = m;
    if(!success) {
        if(target_val < arr[0] || target_val > arr[ct - 1])
            idx = -1;
    }
    return idx;
}

// Append Unique
void im_append_unique(export int arr[]; const int val) {
    if(find(arr, val) < 0)
        append(arr, val);
}
void im_append_unique(export float arr[]; const float val) {
    if(find(arr, val) < 0)
        append(arr, val);
}
void im_append_unique(export vector2 arr[]; const vector2 val) {
    if(find(arr, val) < 0)
        append(arr, val);
}
void im_append_unique(export vector arr[]; const vector val) {
    if(find(arr, val) < 0)
        append(arr, val);
}
void im_append_unique(export vector4 arr[]; const vector4 val) {
    if(find(arr, val) < 0)
        append(arr, val);
}
void im_append_unique(export string arr[]; const string val) {
    if(find(arr, val) < 0)
        append(arr, val);
}
void im_append_unique(export string str; const string val) {
    if(find(str, val) < 0)
        append(str, val);
}

// Make Array Unique
int[] im_unique_arr(const int arr[]) {
    int new_arr[] = {};
    foreach(int val; arr)
        im_append_unique(new_arr, val);
    return new_arr;
}
float[] im_unique_arr(const float arr[]) {
    float new_arr[] = {};
    foreach(float val; arr)
        im_append_unique(new_arr, val);
    return unique_arr;
}
vector2[] im_unique_arr(const vector2 arr[]) {
    vector2 new_arr[] = {};
    foreach(vector2 val; arr)
        im_append_unique(new_arr, val);
    return new_arr;
}
vector[] im_unique_arr(const vector arr[]) {
    vector new_arr[] = {};
    foreach(vector val; arr)
        im_append_unique(new_arr, val);
    return new_arr;
}
vector4[] im_unique_arr(const vector4 arr[]) {
    vector4 new_arr[] = {};
    foreach(vector4 val; arr)
        im_append_unique(new_arr, val);
    return new_arr;
}
string[] im_unique_arr(const string arr[]) {
    string new_arr[] = {};
    foreach(string val; arr)
        im_append_unique(new_arr, val);
    return new_arr;
}
string im_unique_arr(const string str) {
    string new_str = "";
    foreach(string val; str)
        im_append_unique(new_str, val);
    return new_str;
}

#endif
