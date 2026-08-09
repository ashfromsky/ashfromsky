import sys

USER_INPUT = r"""                                                                                      
                                                                                      
                                                                                      
                                                                                      
                                                                                      
                                                                                      
                                                                                      
                                                                                      
                                  Xfxcc                                               
                                 1_)jXx?~)nv                                          
                                ]??|(rOCvx[rv                                         
                                ]_tLpO0dXLUut                                         
                               ~\f-i>|Zwbwqnf                                         
                               >xuwmmxw|0Uw{                                          
                               _/)vL\LphdpwQ                                          
                                n(\+fpkZqZZC                                          
                                \)z_]YmwO                                             
                               n[]][Cwzf                                              
                            _,](??-~]0dO_                                             
                          "^""i--_-[Cwdqi{                                            
                      r(tc~^^^^_?{(xQ0qk+_-]                                          
                   r}?][[jl++:<~dbbpbbd~+__~ccxJ                                      
                 (>">[|cn_^,lf_<0qbdpd<+_-+?t1_(nn                                    
                x;:l1,!n{!zI/~;_-dpbd++~~>""ti\txXx                                   
                ?Ilvv`!r<!}>;!~~~?dd+_+~z~[~/1~n(~J+                                  
                >l;i>`!f~!ii!!i<{>)?i>~~<<_<it<j?-j_                                  
               Q^!l!n`->}vCz}ii<(<_|f<<<><<<!~~>?>-_?                                 
               >;;{1x^}i<ixYY!i>_"+n]<~<YLQ~fc/+}x__+                                 
              {,l!l11^1L>>QcXYi>+>~u><~Xcb!i!\rz+YY-j)                                
              ,!<I!!'<t>\UfOr|l>1<<<>~tcCriij~i>:u_---                                
             !I![>i>^i)<>/J-j\i<\~~_~+mO(nXilx1~1~<j?|_                               
            !ili!+>|';/<<CU)J}l+1~~}_~XQQQ>I)j>~)Y<_/-[|                              
            )|~[<<i`.;i>>?L/X/lc<<<z~?YuYO!;jrf?i<1~[[Jx                              
              ,i>\[..II>UvCJrn!tl{{j+X|zx>I}-j<^l!j-_+XYx                             
               ?i;^.'lli+YQu[jl<i~u-[YYJxc!u{-~`^;(<?->>                              
               ?fL}I':liQ)mcY)!i><n~+XvQC:i+|1u'`;Qbdq                                
                {YC>.,!<_~<uUi!!~i~~~z}?c~><]-[^iOpdp                                 
                -r0?^^:Itu+~<!i!+i<_~+zi";~}r+~"cddpc                                 
                 [v[i'l]|\[}<ii:+>j+_?~;t?-^[{>fqddY                                  
                 ]vU-`^,ifx1~i[;~[|~+]n{<r\"<[|pddQ                                   
                  {xO-,'^,z\~>/l~n++-j\_{rOdbdpddw                                    
                  -rXLq_+?~r<ii"!(<+~{\1nZ+OddqqZ                                     
                   ]]CQ;^l+-~iti'<<-<;>>I>njqwpc                                      
                   +_|n},\}(Xx\<^"^!_1-:nux/\O_                                       
                    --1X^`+__+~+;:!lI>[rfjrXnc[                                       
                    :<{\I"l/!""I\"^`^]/frxrvuc                                        
                   !,t/cx|uXXXnrclj""-ffnunvzz                                        
                    _tuYcjcXXcurxl1,"-jjxvvczz                                        
                   ?l<jnrvcYYcuu>l,,^~frrvucY                                         
                    Ii\//rrxnvnv!l,,^-rxxuucY                                         
                   II<\)juzzcvnv'::,^[rrnnuXz                                         
                   :I-tfvcvxftv<'::,"{rxxnuXY                                         
                    I]jxvczczcX`'::,,(xxnucYz                                         
                    I]tnnczzvXX^',;:;\jjxncXY                                         
                    I}t/trvzzYci`^::i\jfjnzXJ                                         
                    ;>/|rvYvzUzz^`,:+tj/(xcXu                                         
                     ;(u\}tXJJYXI'^,?tr(1ncz}                                         
                     Iixct1/uzcYc'`l]j/~|uvY                                          """

# Strip leading/trailing empty lines
lines = USER_INPUT.splitlines()
non_empty_lines = [l for l in lines if l.strip()]

print(f"Original lines count: {len(lines)}")
print(f"Non-empty lines count: {len(non_empty_lines)}")

min_indent = min(len(l) - len(l.lstrip()) for l in non_empty_lines)
max_right = max(len(l.rstrip()) for l in non_empty_lines)

print(f"Min indent: {min_indent}, Max right: {max_right}")

cropped_lines = [l[min_indent:max_right] for l in non_empty_lines]
content_width = max_right - min_indent
print(f"Bounding box size: {len(cropped_lines)} lines x {content_width} cols")

TARGET_H = 25
TARGET_W = 40

step_y = len(cropped_lines) / float(TARGET_H)
step_x = content_width / float(TARGET_W)

downscaled = []
for i in range(TARGET_H):
    y_idx = min(int(i * step_y), len(cropped_lines) - 1)
    line = cropped_lines[y_idx]
    row_chars = []
    for j in range(TARGET_W):
        x_idx = min(int(j * step_x), len(line) - 1)
        char = line[x_idx] if x_idx < len(line) else " "
        row_chars.append(char)
    downscaled.append("".join(row_chars))

with open("assets/ascii_dark.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(downscaled))

with open("assets/ascii_light.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(downscaled))

print("Downscaled ASCII preview:")
for idx, l in enumerate(downscaled):
    print(f"{idx:02d}: |{l}|")
