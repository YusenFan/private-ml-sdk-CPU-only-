1. Figure the LLM model api 

2. Figure out the resource part 3
3. Figure out the attestation part 
4. VectorDB
    a. K-D tree
    b. if its secure if using S3 
what is the embedding structure of gemma3 
what is the relationship between VectorDB and LLM when querying (how to make sure its secured)


question list:
what is Dstack, what does it do?
SDK that help deploy applicaiton into Tees. 


what is https://inference-api.phala.network do? 
Its a testing api for attested llm inference..


dose the local KMS requrie to use GPU?
no

what is Quote mean in attestation or in intel ?
its a data structure for signed data


so e2e.py is actually act as client/user to do api call(chat complation) 

The initial Attestation is a one time/per session thing
after the trust is established, the user can communicate with TEE.



the response will be cached for 5 minutes, (what happened here?)

the attestation will only be valid for 5mins


how does the remote attestation work?


Client side need to verify is it connect to a real TEE
1. Send the request to TEE to get TDX quote and bind public key for verification 

curl -H "Authorization: Bearer <your-token>" \
     https://<your-tee-domain>/v1/attestation/report

2. in client side use Intel DCAP library to verify 

3. recoerd the signing address or only identify key for the session

4. send vllm-proxy or upload the confidential document to the server

