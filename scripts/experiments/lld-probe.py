import os,subprocess,json
from pathlib import Path
root=Path.cwd(); out=Path('/tmp/lld-probe'); rows=[]
(out/'probe.rs').write_text('fn main() { println!("LLD probe OK"); }')
for target in ['x86_64-unknown-linux-gnu','aarch64-unknown-linux-gnu']:
 toolchain=out/target
 script="const fs=require('fs');const {download}=require('/tmp/lld-probe/node_modules/@napi-rs/cross-toolchain');fs.mkdirSync(process.argv[1],{recursive:true});download('x64',process.argv[2]).unpack(process.argv[1]);"
 subprocess.run(['node','-e',script,str(toolchain),target],check=True)
 env={**os.environ,'RUST_TARGET':target,'TARGET_SYSROOT':str(toolchain/target/'sysroot')}
 binary=out/(target+'.bin')
 cmd=['rustc',str(out/'probe.rs'),'--target',target,'-Zunstable-options','-Clinker-flavor=gnu-lld-cc','-Clink-self-contained=+linker','-Clinker='+str(root/'scripts/linux-cross-linker.sh'),'-o',str(binary)]
 subprocess.run(cmd,check=True,env=env)
 comment=subprocess.check_output(['readelf','-p','.comment',str(binary)],text=True)
 assert 'LLD' in comment
 row={'target':target,'comment':comment,'file':subprocess.check_output(['file',str(binary)],text=True)}
 if target.startswith('x86_64'): row['runtime']=subprocess.check_output([str(binary)],text=True)
 rows.append(row)
 (out/'results.json').write_text(json.dumps(rows,indent=2));print(row,flush=True)
# Native Cargo uses the target configuration without NAPI or the wrapper.
subprocess.run(['cargo','new','--bin',str(out/'native')],check=True)
subprocess.run(['cargo','build','--manifest-path',str(out/'native/Cargo.toml'),'--target','x86_64-unknown-linux-gnu'],check=True,cwd=root)
comment=subprocess.check_output(['readelf','-p','.comment',str(out/'native/target/x86_64-unknown-linux-gnu/debug/native')],text=True)
assert 'LLD' in comment
rows.append({'native_cargo':comment});(out/'results.json').write_text(json.dumps(rows,indent=2))
